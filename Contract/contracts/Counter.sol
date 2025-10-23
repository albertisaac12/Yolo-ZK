// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.28;

contract ZKBioRegistry {

  event Commitment(uint256 indexed id,uint256 indexed p_hash);
  error InvalidCommiter();

  mapping(uint256=>uint256) private commitments;

  address public commiter;

  modifier hasRole {
    if(msg.sender!=commiter) revert InvalidCommiter();
    _;    
  }

  function commit(uint256 id, uint256 p_hash) external hasRole{
    emit Commitment(id,p_hash);
    commitments[id] = p_hash;
  }

  function reterieve(uint256 id) external view returns(uint256){
    return commitments[id];
  }


}