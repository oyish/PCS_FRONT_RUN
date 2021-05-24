from bot import Bot
from time import sleep, time

bot = Bot("mainnet")

my_bnb = 0.1
MAX_RETRY = 3
while True:
    st = bot.block
    pendings = bot.reader.get_pends()
    if len(pendings) > 0:
        tx = pendings[0]
        dead = tx['args']['deadline']
        gap = (dead - time()) % 60
        val = tx['value'] if tx['value'] / 1e18 < my_bnb else my_bnb * 1e18
        profit = val * (tx['rate'] / 100) / 1e18
        ed = bot.block
        if profit < 0.004 or st != ed:
            continue
        tx = pendings[0]
        print(f"[BOT] - TRADE DETECTED    GAP : {gap} RATE:{tx['rate']} // VALUE:{tx['value']} // GAS:{tx['gas']} ")
        buy_amount = tx['value']
        buy_token = tx['path'][-1]
        if bot.check_black_list(buy_token):
            print(f"[BOT] - BLACKLISTED TOKEN. Next.")
            continue
        buy_tx = bot.sender.buy(buy_amount, buy_token, tx['to'], tx['gas'] + 2)
        block_num = bot.block
        print(f"[BOT] - Buy {buy_token}. ROUTER : {tx['to']}  GAS : {tx['gas'] + 2} HASH : {buy_tx}")

        retry = 0
        nonce = 1
        gas_addi = 1
        while True:
            if block_num < bot.block:
                if retry > 0:
                    print(f"[BOT] - Sell Retry.")
                    sell_tx = bot.sender.emergencySell(buy_token, tx['to'], tx['gas'] + gas_addi, nonce=nonce)
                else:
                    sell_tx = bot.sender.sell(buy_token, tx['to'], tx['gas'] + gas_addi, nonce=nonce)
                retry += 1
                nonce = 0
                print(f"[BOT] - Sell {buy_token}. GAS : {tx['gas'] + gas_addi} HASH : {sell_tx}")
                buy_status = 0
                ipend = 0
                while not bot.end_pending(sell_tx):
                    buy_pending = bot.end_pending(buy_tx)
                    if buy_pending is False:
                        print("[BOT] - Failed to Buy Order. reset BOT.")
                        break
                    if buy_pending:
                        try:
                            buy_status = bot.get_status(buy_tx)
                            if buy_status != 1:
                                print("[BOT] - Failed to Buy Order. reset BOT.")
                        except:
                            pass
                    ipend += 1
                    if ipend % 200 == 0:
                        print("[BOT] INFINITE PENDING.... ")
                        bot.add_black_list(buy_token)
                        nonce = 1
                        gas_addi += 1
                        break
                    sleep(0.5)
                buy_status = bot.get_status(buy_tx)
                if buy_status != 1:
                    print("NEXT,")
                    break
                sleep(3)
                sell_status = bot.get_status(sell_tx)
                if sell_status == 1:
                    print(f"[BOT] - End Pending Sell. HASH : {sell_tx}")
                    break
                elif buy_status != 1:
                    print(f"[BOT] - Buy Failed. (failed)HASH => {sell_tx}")
                    break
                elif buy_status == 1 and sell_status != 1 and retry > MAX_RETRY:
                    sell_tx = bot.sender.emergencySell(buy_token, tx['to'], tx['gas'] + 1, nonce=nonce)
                    print(f"[BOT] - Sell Fail. Emergency Selling => {sell_tx}")
                    while bot.end_pending(sell_tx):
                        sleep(0.5)
                    print(f"[BOT] - EmergencySell End Pending HASH => {sell_tx}")
                    bot.add_black_list(buy_token)
                    break
                else:
                    print("FAIL TO SELL - ", sell_status)
                    block_num = bot.block
