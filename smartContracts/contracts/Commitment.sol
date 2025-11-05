// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

abstract contract StateVars {
  event Commitment(string indexed id,uint256 indexed p_hash);
  error InvalidCommiter();
  mapping(string=>uint256) internal commitments;
  address public commiter;

  modifier hasRole {
    if(msg.sender!=commiter) revert InvalidCommiter();
    _;    
  }
  constructor(address _commiter) {
    commiter = _commiter;
  }
}

contract ZKBioRegistry is StateVars{

  constructor (address _commiter) StateVars(_commiter) {}

  function commit(string memory id, uint256 p_hash) external hasRole{
    emit Commitment(id,p_hash);
    commitments[id] = p_hash;
  }

  function reterieve(string memory id) external view returns(uint256){
    return commitments[id];
  }

  function updateCommitter(address newCommitter) external hasRole {
    commiter = newCommitter;
  }


}