from multiprocessing.sharedctypes import Value
import random
import timeit


# These are the dictonaries that contain information on each possible prize on said prize table.
# The odds were taken from the in-game information of chances of rolling said prize as a whole then recaculated into the value of rolling that prize in the gem table.
# An example would be the 50 Mil Cash bag...

# The odds of rolling a 50 Mil Cash bag overall was stated to be 0.002 in the game interface, all Purple gems totaled equaled a chance to roll a Red gem as 1.885...
# assuming a Purple Gem is rolled the proportion to roll the 50 Mil Cash prize would be...
# 0.002 over 1.885 = x over 100
# 0.002 =  x
# 1.885 = 100
# (0.002 * 100)/1.885 = 0.1061007957559682 over 100 chance to roll the 50Mil Cash bag on the Purple Gem Table.
# Values were rounded up to the nearest thousands.

# The functions used needed to equal 100% so in some small cases I did take very small thousands either off the top of the tables, or added to the bottom.
# This should skew the values very very very very very very very very slightly downwards.

# Yellow Prize Name && weight
yellowGemPrizes =   {
                'lamp': 10.159,
                'star': 12.44,
                'proteans': 8.904,
                'cashBag': 6.478,
                'spring': 4.178,
                'silverhawk': 4.178,
                'skillPack': 4.178,
                'magicNote': 4.178,
                'D&DweekReset': 4.178,
                'tokenBox': 4.178,
                'combatDummy': 11.635,
                'spiritDragonstone': 11.635,
                'divineLocation': 13.681
                }

# Orange Prize Name && weight
orangeGemPrizes = {
                'lamp':14.32,
                'star':17.531,
                'proteans':12.347,
                'cashBag':1.992,
                'spring':4.54,
                'silverhawk':4.54,
                'skillPack':4.54,
                'magicNote':4.54,
                'D&DmonthReset':4.54,
                'tokenBox':4.54,
                'combatDummy':12.654,
                'spiritOnyx':12.654,
                'mediumSkillCrate':1.262
                }

# Red Prize Name && weight
redGemPrizes = {
                'lamp':28.0103,
                'star':30.485,
                'proteans':11.649,
                'cashBag':2.0137,
                'spring':5.272,
                'silverhawk':5.272,
                'skillPack':5.272,
                'cinderCore':5.272,
                'advancedPulseCore':5.272,
                'largeSkillCrate':1.482
                }

# Purple Prize Name && weight
purpleGemPrizes = {
                'lamp':29.496,
                'star':36.127,
                'proteans':12.626,
                'cashBag':1.91,
                'cashBag50mil':0.106,
                'spring':6.048,
                'silverhawk':6.048,
                'skillPack':6.048,
                'largeSkillCrate':1.591
                }

# Blue Prize Name && weight
blueGemPrizes = {
                'supKnowlegeBombs':25,
                'boxDeathtoughDart':25,
                'boxProteanProc':25,
                'boxDummyProc':25,
                }

# These are the Gems that were availible in the Promo.
# This is a list of dictionaries containing gem names, weighted odds of rolling the gem, oddment payout for the game both prize and converting
# and another dictionaries in the prizes, this contained the possible prize rolls for that gem along with the odds of rolling that prize if said gem was rolled
foresightPromoGems = [
    {
        'name': 'fairlyCommon',
        'gemWeight': 66.827,
        'oddments': (25, 60),
        'prizes': yellowGemPrizes
    },
    {
        'name':'uncommon',
        'gemWeight': 24.095,
        'oddments': (50, 120),
        'prizes': orangeGemPrizes
    },
    {
        'name': 'rare',
        'gemWeight': 7.151,
        'oddments': (100, 300),
        'prizes': redGemPrizes
    },
    {
        'name': 'veryRare',
        'gemWeight': 1.885,
        'oddments': (250, 850),
        'prizes': purpleGemPrizes
    },
    {
        'name':'ultraRare',
        'gemWeight': 0.004,
        'oddments': (500, 1750),
        'prizes': blueGemPrizes
    }
]

## Function used to calculate oddment payouts, used in the case of evaluating prizes Vs. Prize. 
# I felt this was a good way for comparing multi gem prize rolls such as 5x Orange/Uncommon Vs. 1 Red Prize
def calcOddments(oddmentsSet: set, multi: int) -> int:
    return oddmentsSet[1] * multi + oddmentsSet[0]

## Used to attempt to pick the best prize from a 3 Prize TH Key roll. Uses the calcOddments(), but is set to always override a Blue Vs. Anything else.
## A Blue Prize Vs. a Blue Prize should be astronamically Rare, but will compare Oddment value if needed in the case of Multiroll like 1 blue Vs. 5 Blue
def pickAPrize(prizeList: list):
    ## Sets Default best prize to the first in the list
    highestOddmentsPrize = prizeList[0]

    x = 0
    ## Loop the other 2 values
    while x < len(prizeList) - 1:
        ## Override if a blue is found to make it auto best. Will skip if they are both blue and compare oddments.
        if highestOddmentsPrize[0].get('name') != 'ultraRare' and prizeList[x+1][0].get('name') == 'ultraRare':
            highestOddmentsPrize = highestOddmentsPrize
            highestOddmentsPrize = prizeList[x+1]
        elif calcOddments(highestOddmentsPrize[0].get('oddments'), highestOddmentsPrize[2]) >= calcOddments(prizeList[x + 1][0].get('oddments'), prizeList[x + 1][2]):
            highestOddmentsPrize = prizeList[x]
        else:
            highestOddmentsPrize = prizeList[x + 1]
        
        x+=1
    ## return best prize
    return highestOddmentsPrize

## Takes number of keys to run for promo, return prizes
def foresightPromo(keys: int) -> list:
    gemList = []
    gemWeightList = []
    ## unpack gem list name keys, and weights of gem
    for x in (foresightPromoGems):
        ## Unpacks the GemList names and weights into 2 lists, just makes it easier to read.
        gemList.append(x.get('name'))
        gemWeightList.append(x.get('gemWeight'))

    finalPrizePicked = []
    ## Runs loop for each key
    for i in range(keys):
        ## Returns a 3 item list, foresightPromoGems are the availbile gems, gemWeightList are the weighted odds of rolling said gem.
        ## This will essentially Roll the 3 possible Gems/Chests for your 1 Key. Prizes rolled next.
        gemsRolled = random.choices(foresightPromoGems, weights=gemWeightList, k = 3)
            

        prizesRolled = []
        ## Nested For each Gem rolled above a similar thing is Done here 1 at a time for the chosen Gem on its prize table.
        ## .pop() is used because choices always returns a list even when k values is not given, and I did not want a nested list here.
        for gemRolled in gemsRolled:
            prizeRoll = random.choices(list(gemRolled.get('prizes').keys()), weights=list(gemRolled.get('prizes').values())).pop()

            # Random choice of 1-5, Equal Chance no info found on higher being lower odds.
            multiRolled = random.choices([1, 2, 3, 4, 5]).pop()
            # Creates a Set of the info
            prizeRollInfo = (gemRolled, prizeRoll, multiRolled)
            # Adds gem/prize info to prizesRolled list for later.
            prizesRolled.append(prizeRollInfo)

        ## The Best prize for the set of 3 from above is input into the pickAPrize() function, appends returned prize to final prizes list
        finalPrizePicked.append(pickAPrize(prizesRolled))
    # Returns finalPrizesPicked List
    return finalPrizePicked



def runTHsimm(keys: int):
    ## Timer for execution of block of code.
    starttime = timeit.default_timer()
    print("Beginning simulation")

    ## Empty Gem award Dic, Used for totaling up the distrabusion of Gems returned
    gemsAwarded = {
                ##'common':0,
                'fairlyCommon':0,
                'uncommon':0,
                'rare':0,
                'veryRare':0,
                'ultraRare': 0
                }

    ## Empty Prize Dic of Dics, used for totaling up the distrabusion of Prizes Returned 
    prizesAwarded = {
                'fairlyCommon':{},
                'uncommon':{},
                'rare':{},
                'veryRare':{},
                'ultraRare': {}
                }

    # calls foresightPromo() function, inputs keys to run on the promo
    returnedGemPrizes = foresightPromo(keys)

    ## Loops the returned returnedGemPrizes to Add to the Gem dic and Prize lists. Used to see How many Gems were rolled since prizes can award up to 5 per Gem.
    for prize in returnedGemPrizes: 
        gemsAwarded[prize[0].get('name')] = gemsAwarded[prize[0].get('name')] + 1

        ## Adds to Prize Dic, more code cause did not want to make Giant empty award List atm. Results not necessarily sorted.
        if prize[1] in prizesAwarded.get(prize[0].get('name')):
            prizesAwarded[prize[0]['name']][prize[1]] += prize[2]
        else:
            prizesAwarded[prize[0]['name']][prize[1]] = prize[2]



    # print output of GemsAwarded
    for key, value in gemsAwarded.items():
        print(f"{key}: {value}")

    ## Just a lazy line break =)
    print()
    # Print out prizes awarded
    for key, value in prizesAwarded.items():
        print(f'{key} gem prizes awarded:'.upper())
        for prize, amount in value.items():
            print(f"    - {prize}: {amount}")
        print()
    


    # timer end time, prints time it took to execute code on local machine.
    print("Execution time:", timeit.default_timer() - starttime)


## Change this to decide how many keys to run in the sim. 

keys = 1000000
runTHsimm(keys)




