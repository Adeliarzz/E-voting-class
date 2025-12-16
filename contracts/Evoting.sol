// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Evoting {
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    mapping(uint => Candidate) public candidates;
    mapping(address => bool) public hasVoted;
    uint public candidatesCount;
    address public admin;

    event VoteCast(address indexed voter, uint indexed candidateId);
    event CandidateAdded(uint id, string name);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function addCandidate(string memory _name) public onlyAdmin {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
        emit CandidateAdded(candidatesCount, _name);
    }

    // Custodial Vote: Admin submits on behalf of _voter
    function vote(address _voter, uint _candidateId) public onlyAdmin {
        require(!hasVoted[_voter], "Voter has already voted");
        require(
            _candidateId > 0 && _candidateId <= candidatesCount,
            "Invalid candidate ID"
        );

        hasVoted[_voter] = true;
        candidates[_candidateId].voteCount++;

        emit VoteCast(_voter, _candidateId);
    }

    function getCandidate(
        uint _id
    ) public view returns (uint, string memory, uint) {
        Candidate memory c = candidates[_id];
        return (c.id, c.name, c.voteCount);
    }
}
