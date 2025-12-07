// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ClassVote {
    address public admin;
    bool public votingOpen;

    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    mapping(uint => Candidate) public candidates;
    uint public candidatesCount;

    mapping(address => bool) public hasVoted;

    event CandidateAdded(uint id, string name);
    event Voted(address voter, uint candidateId);
    event VotingOpened();
    event VotingClosed();

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier whenOpen() {
        require(votingOpen == true, "Voting is not open");
        _;
    }

    constructor() {
        admin = msg.sender;
        votingOpen = false;
    }

    function addCandidate(string memory _name) public onlyAdmin {
        candidatesCount++;
        candidates[candidatesCount] = Candidate(candidatesCount, _name, 0);
        emit CandidateAdded(candidatesCount, _name);
    }

    function openVoting() public onlyAdmin {
        votingOpen = true;
        emit VotingOpened();
    }

    function closeVoting() public onlyAdmin {
        votingOpen = false;
        emit VotingClosed();
    }

    function vote(uint _candidateId) public whenOpen {
        require(!hasVoted[msg.sender], "You already voted");
        require(_candidateId > 0 && _candidateId <= candidatesCount, "Invalid candidate");

        hasVoted[msg.sender] = true;
        candidates[_candidateId].voteCount++;
        emit Voted(msg.sender, _candidateId);
    }
}