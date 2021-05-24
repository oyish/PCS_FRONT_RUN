pragma solidity >=0.6.6;

import "https://github.com/pancakeswap/pancake-swap-periphery/blob/master/contracts/interfaces/IPancakeRouter01.sol";
import "https://github.com/pancakeswap/pancake-swap-periphery/blob/master/contracts/interfaces/IPancakeRouter02.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol";
import "https://github.com/pancakeswap/pancake-swap-core/blob/master/contracts/interfaces/IPancakeFactory.sol";
import "https://github.com/pancakeswap/pancake-swap-core/blob/master/contracts/interfaces/IPancakePair.sol";

contract MyBot {
    address internal constant PANCAKE_TEST_ROUTER_ADDRESS = 0x9Ac64Cc6e4415144C455BD8E4837Fea55603e5c3;
    address internal constant PANCAKE_TEST_FACTORY_ADDRESS = 0xB7926C0430Afb07AA7DEfDE6DA862aE0Bde767bc;
    address internal constant PANCAKE_ROUTER_V1_ADDRESS = 0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F;
    address internal constant PANCAKE_ROUTER_V2_ADDRESS = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
    address internal constant PANCAKE_FACTORY_V1_ADDRESS = 0xBCfCcbde45cE874adCB698cC183deBcF17952812;
    address internal constant PANCAKE_FACTORY_V2_ADDRESS = 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73;

    IPancakeRouter02 public pcsRouter;
    uint constant MAX_UINT = 2**256 - 1;
    mapping (address => uint[2]) resv;
    mapping (address => uint) pendingWithdrawals;
    address payable owner;

    event Received(address sender, uint amount);

    constructor() public{
        pcsRouter = IPancakeRouter02(PANCAKE_TEST_ROUTER_ADDRESS);
        owner = payable(msg.sender);
    }

    modifier onlyOwner {  // 계약서 배포자 계정만 실행할 수 있도록 제한하는 Modifier1 정의
       require(
           msg.sender == owner, "Only owner can call this function."
       );
       _;
   }

    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    function getReserves(address[] memory tokenAddress, address[] memory routerAddress) public view returns(uint[] memory resv0, uint[] memory resv1){
        uint[] memory resv0 = new uint[](tokenAddress.length);
        uint[] memory resv1 = new uint[](tokenAddress.length);
        uint resv_0;
        uint resv_1;
        for(uint i=0;i<tokenAddress.length;i++){
            (resv_0, resv_1) = getReserve(tokenAddress[i], routerAddress[i]);
            resv0[i] = resv_0;
            resv1[i] = resv_1;
        }
        // 0x223Fb59bF5C8724d7D7a1Dc4D655D13F293342f8
        return (resv0,resv1);
    }

    function getReserve(address tokenAddress, address routerAddress) public view returns(uint resv0, uint resv1){
        address factoryAddress;
        if(routerAddress == PANCAKE_ROUTER_V1_ADDRESS){
            factoryAddress = PANCAKE_FACTORY_V1_ADDRESS;
        }else if (routerAddress == PANCAKE_ROUTER_V2_ADDRESS){
            factoryAddress = PANCAKE_FACTORY_V2_ADDRESS;
        }
        IPancakeFactory factory = IPancakeFactory(factoryAddress);
        IPancakeRouter02 router = IPancakeRouter02(routerAddress);
        IPancakePair pair;
        address pairAddress = factory.getPair(router.WETH(), tokenAddress);
        pair = IPancakePair(pairAddress);
        (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast) = pair.getReserves();
        uint resv0;
        uint resv1;
        if(router.WETH() == pair.token0()){
            resv0 = reserve0;
            resv1 = reserve1;
        }
        else
        {
            resv0 = reserve1;
            resv1 = reserve0;
        }
        return (resv0, resv1);
    }

    function buyToken(uint ethAmount, address tokenAddress, address routerAddress) public payable onlyOwner {
        uint buyAmount;

        // if ethAmount > balance then change ethAmount to address balance
        if(ethAmount > address(this).balance){
            buyAmount = address(this).balance;
        }else{
            buyAmount = ethAmount;
        }
        require(buyAmount <= address(this).balance, "Not enough ETH");
        IERC20 token = IERC20(tokenAddress);
        if(token.allowance(address(this), routerAddress) < 1){
            require(token.approve(routerAddress, MAX_UINT),"FAIL TO APPROVE");
        }
        address spender = routerAddress;
        IPancakeRouter02 router = IPancakeRouter02(routerAddress);
        address[] memory path = new address[](2);
        path[0] = router.WETH();
        path[1] = tokenAddress;
        router.swapExactETHForTokens{value: buyAmount}(0, path, address(this), block.timestamp+60);
    }

    function sellToken(address tokenAddress, address routerAddress) public onlyOwner payable {
        IERC20 token = IERC20(tokenAddress);
        IPancakeRouter02 router = IPancakeRouter02(routerAddress);
        address[] memory path = new address[](2);
        path[0] = tokenAddress;
        path[1] = router.WETH();
        uint tokenBalance = token.balanceOf(address(this));
        if(token.allowance(address(this), routerAddress) < tokenBalance){
            require(token.approve(routerAddress, MAX_UINT),"FAIL TO APPROVE");
        }
        router.swapExactTokensForETH(tokenBalance,0,path,address(this),block.timestamp+60);
    }

    function emergencySell(address tokenAddress, address routerAddress) public onlyOwner payable returns (bool status){
        IERC20 token = IERC20(tokenAddress);
        uint tokenBalance = token.balanceOf(address(this));
        if(token.allowance(address(this), routerAddress) < tokenBalance){
            require(token.approve(routerAddress, MAX_UINT),"FAIL TO APPROVE");
        }
        IPancakeRouter02 router = IPancakeRouter02(routerAddress);
        address[] memory path = new address[](2);
        path[0] = tokenAddress;
        path[1] = router.WETH();
        router.swapExactTokensForETHSupportingFeeOnTransferTokens(tokenBalance, 0, path, address(this), block.timestamp+60);
        return true;
    }

    function withdraw() public onlyOwner payable{
        uint amount = pendingWithdrawals[msg.sender];
        // 리엔트란시(re-entrancy) 공격을 예방하기 위해
        // 송금하기 전에 보류중인 환불을 0으로 기억해 두십시오.
        pendingWithdrawals[msg.sender] = 0;
        owner.transfer(address(this).balance);
    }

    function withdrawToken(address tokenAddress, address to) public payable onlyOwner returns (bool res){
        IERC20 token = IERC20(tokenAddress);
        bool result = token.transfer(to, token.balanceOf(address(this)));
        return result;
    }
}
