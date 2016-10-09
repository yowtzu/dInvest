web3.eth.defaultAccount = "0xC5edcA9161B6eb16da20A8bb103233A536Aa7b42"
personal.unlockAccount(web3.eth.defaultAccount, "Qzxw@1234")
var source = "pragma solidity ^0.4.0;contract HedgeContract1 { struct Investment { address investor; uint value; uint nowValue; uint period; uint withdrawalLimit; } address public creator; address public investAgent; address public buyAgent; uint public minimumInvestment; mapping(address => Investment) public investments;  event InvestmentMade(address accountAddress, uint amount);  modifier onlyBy(address _account) { if (msg.sender != _account) throw; _; } function HedgeContract1( uint _minimumInvestment, address _investAgent, address _buyAgent ) {  creator = msg.sender; }  function setInvestAgent(address newInvestAgent) onlyBy(creator) { investAgent = newInvestAgent; }  function setBuyAgent(address newBuyAgent) onlyBy(creator) { buyAgent = newBuyAgent; }  function setMinimumInvestment(uint newMinimumInvestment) onlyBy(creator) { minimumInvestment = newMinimumInvestment; }  function createInvestment() payable { if (msg.value < minimumInvestment) { throw; } investments[msg.sender] = Investment(msg.sender, msg.value, msg.value, 3, 1); }   function investOffer(address account, uint amount, bool invest) onlyBy(investAgent) {  if (invest) { InvestmentMade(account, amount);  } else { throw; } }  function afterInvestOffer(address account, uint amount) onlyBy(investAgent) { investments[account].nowValue = amount; }  function kill() { if (msg.sender == creator) suicide(creator); }}"
var compiled = web3.eth.compile.solidity(source)
var contractC = web3.eth.contract(compiled.HedgeContract1.info.abiDefinition)
var hedge = contractC.at("0x506d594D4bcE3D8f3cACE1eAB0Cd507b592e3bb4")
