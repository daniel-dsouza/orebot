import argparse
import discord
from discord.ext import commands

from valuation import best_guess, get_mineral_value, get_ore_value

parser = argparse.ArgumentParser()
parser.add_argument('token', help='your discord bot token')
parser.add_argument('-p', '--prefix', help='prefix for commands')
args = parser.parse_args()

bot = commands.Bot(command_prefix='!orebot ')

@bot.event
async def on_ready():
    """ Confirms the identity of the bot. """
    print('logged in as {}: {}'.format(bot.user.name, bot.user.id))


@bot.command()
async def ore_value(ore, amount: int):
    """ Calculates ore value based on ore prices """
    ore_name = best_guess(ore)

    try:
        assert amount > 0
    except AssertionError:
        await bot.say('You must have positive ore!')
        return

    appraisal = get_ore_value(ore_name, amount) * 0.90
    await bot.say("I'd say {} units of '{}' is worth {:,.0f} ISK at 10% below Jita ore prices".format(amount, ore_name, appraisal))


@bot.command()
async def mineral_value(ore, amount: int, efficiency: int):
    """ Calculates ore value based on mineral prices """
    ore_name = best_guess(ore)
    
    try:
        assert amount > 0
    except AssertionError:
        await bot.say('You must have positive ore!')
        return

    try:
        assert efficiency > 0 and efficiency < 100
    except AssertionError:
        await bot.say('efficiency must be between 0 and 100%')
        return

    appraisal = get_mineral_value(ore_name, amount, efficiency/100) * 0.90
    await bot.say('I\'d say {} units of "{}" is worth {:,.0f} ISK at 10% below Jita mineral prices'.format(amount, ore_name, appraisal))


if __name__ == '__main__':
    bot.run(args.token)
