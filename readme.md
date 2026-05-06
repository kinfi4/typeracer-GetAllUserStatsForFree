# Get User Stats for TypeRacer

#### Are you a greedy piece of shit, and you dont want to pay 12$ annually for typeracer.... just like me? But you still wanna see your account statistics?
Lucky for you, I have a solution to our problem. I have written a small script for deep parsing and analysis stats data from typeracer, and I d like to share it with you. All you need is installed python3 on your computer. 

Script can also plot some general information for you, if you wanna something unusual, you free to use csv file that will be created.


-------------------------------
## How to use?
        
        git clone https://github.com/kinfi4/typeracer-GetAllUserStatsForFree.git
        cd typeracer-GetAllUserStatsForFree
        pip install -r requirements.txt (you may also create isolated virtual env for that)
        python get_stats.py -u <your username>

### And thats it!

---------------------------
## Authentication (optional)

By default the script fetches public race data without logging in.
To access a private profile or authenticate as yourself:

1. Copy `.env.example` to `.env`
2. Fill in your TypeRacer username and password
3. Run the script as normal — it will log in automatically

        cp .env.example .env
        # edit .env and set TYPERACER_USERNAME and TYPERACER_PASSWORD

---------------------------
## Script arguments:
        * -u (--username) - Username of the account to parse info about
        * -f (--filename) - Filepath where to store the parsed info
            OR file where script can gather info from, if --no-parsing specified
        * -n (--no-parsing) - If it is set script wont parse user stats from typeracer,
            it will use info from file instead. Thats why, if -n was set, you must 
            specify -f (--filename) argument, so script knows where to get info from.
            You may also dont specify -u (--username) argument if --no-parsing set.
        * --hide-plots - Dont show any plots after parsing finished, cant be used together
            with --no-parsing.


@kinfi4
