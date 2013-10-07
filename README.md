Introduction
============

This program attempts to analyze a series of 8-ball Billiards game results and
extract relative player statistics from the data.  In the future, I'd like to
have the program team pairings to have even match-ups in team 8-ball.

Running the samples
===================

 1. Install the needed dependencies with `pip install -r requirements.txt`
 2. Run the analyzer with the sample `bin/analyze -p samples/2-player.json`

Format of the matches file
==========================

The matches file is a JSON file that contains an array of individual match
results.

Ordering players
----------------

### Unknown and partial ordering

For games where it's unknown who broke the rack, there the players are
represented in the file as two teams like this:

    {
        winners: [ "player1", "player3" ],
        losers: [ "player2", "player4" ]
        ... more attributes ...
    }

In the above example, all that's known is that which team one and the players
on each team.  If the ordering of the players is known, then an `ordered`
attribute can be included, like this:

    {
        winners: [ "player1", "player3" ],
        losers: [ "player2", "player4" ],
        ordered: true
        ... more attributes ...
    }

In this example, it's known which team won and that the order of the players
was player1, player2, player3, player4.  It's unknown who broke to start the
match.

### Total order

For games where it's known who broke the rack, a slightly different ordering
is used.  Here is an example match:

    {
        winners: [ "player1", "player2",
                   "player3", "player4" ],
        winning-team: 0
        ... more attributes ...
    }

In this example, it's know that player1 was the person to break the rack and
that the team of player1/player3 won the match.


Match results
-------------

The two resolutions of a match are an 8-ball foul that ends the game early, or
one team winning without a foul.  In both cases, there are some number of balls
left on the table for each team, possibly 0.
