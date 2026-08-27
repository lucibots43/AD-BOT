from highrise import BaseBot, User, Position
from highrise.__main__ import BotDefinition
from asyncio import sleep, create_task, CancelledError
import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
import random
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = "bot_config.json"
DEFAULT_CONFIG = {
    "host_usernames": ["luci.6969"],
    "admin_usernames": ["luci.6969"],
    "vip_usernames": [],
    "banned_users": [],
    "teleport_locations": {
        "vip": {"x": 14.5, "y": 16.75, "z": 5.5},
        "vip1": {"x": 14.5, "y": 16.75, "z": 5.5},
        "dj": {"x": 9.5, "y": 10.75, "z": 10.5}
    },
    "language": "fa",
    "welcome_message": "خوش وامدی! :سازنده بات: @luci.6969",
    "announcement_interval": 300,
    "announcement_message": "برای اجاره بات به آیدی @luci.6969 پیام دهید!"
}

class AdvancedBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.active_users = {}
        self.user_dances = {}
        self.dance_tasks = {}
        self.user_positions = {}
        self.user_scores = {}
        self.user_id = None
        self.announcement_task = None
        self.score_update_task = None
        self.loopchat_task = None
        self.frozen_users = {}
        self.party_dances = {}
        self.commands = {
            "!help": self.cmd_help,
            "!spam": self.cmd_spam,
            "!tele": self.cmd_tele,
            "!heart": self.cmd_heart,
            "!clap": self.cmd_clap,
            "!wink": self.cmd_wink,
            "!wave": self.cmd_wave,
            "!thumbs": self.cmd_thumbs,
            "!wallet": self.cmd_wallet,
            "!set": self.cmd_set,
            "!tip": self.cmd_tip,
            "!vip": self.cmd_vip,
            "!vip1": self.cmd_vip1,
            "!dj": self.cmd_dj,
            "!down": self.cmd_down,
            "!ban": self.cmd_ban,
            "!unban": self.cmd_unban,
            "!dancechain": self.cmd_dancechain,
            "!addtele": self.cmd_addtele,
            "!deltele": self.cmd_deltele,
            "!item set": self.cmd_set_item,
            "!welcome": self.cmd_welcome,
            "!addadmin": self.cmd_addadmin,
            "!removeadmin": self.cmd_removeadmin,
            "!addhost": self.cmd_addhost,
            "!removehost": self.cmd_removehost,
            "!listadd": self.cmd_listadd,
            "!freeze": self.cmd_freeze,
            "!unfreeze": self.cmd_unfreeze,
            "!party": self.cmd_party,
            "!partys": self.cmd_partys,
            "!emotebot": self.cmd_emotebot,
            "!loopchat": self.cmd_loopchat,
            "!lang": self.cmd_lang,
        }
        self.emotes = {
            "1": "idle_zombie","2": "idle_layingdown2","3": "idle_layingdown","4": "idle-sleep",
            "5": "idle-sad","6": "idle-posh","7": "idle-loop-tired","8": "idle-loop-tapdance",
            "9": "idle-loop-sitfloor","10": "idle-loop-shy","11": "idle-loop-sad","12": "idle-loop-happy",
            "13": "idle-loop-annoyed","14": "idle-loop-aerobics","15": "idle-lookup","16": "idle-hero",
            "17": "idle-floorsleeping","18": "idle-enthusiastic","19": "idle-dance-swinging",
            "20": "idle-dance-headbobbing","21": "idle-angry","22": "emote-yes","23": "emote-wings",
            "24": "emote-wave","25": "emote-tired","26": "emote-think","27": "emote-theatrical",
            "28": "emote-tapdance","29": "emote-superrun","30": "emote-superpunch","31": "emote-sumo",
            "32": "emote-suckthumb","33": "emote-splitsdrop","34": "emote-snowball","35": "emote-snowangel",
            "36": "emote-shy","37": "emote-secrethandshake","38": "emote-sad","39": "emote-ropepull",
            "40": "emote-roll","41": "emote-rofl","42": "emote-robot","43": "emote-rainbow",
            "44": "emote-proposing","45": "emote-peekaboo","46": "emote-peace","47": "emote-panic",
            "48": "emote-no","49": "emote-ninjarun","50": "emote-nightfever","51": "emote-monster_fail",
            "52": "emote-model","53": "emote-lust","54": "emote-levelup","55": "emote-laughing2",
            "56": "emote-laughing","57": "emote-kiss","58": "emote-kicking","59": "emote-jumpb",
            "60": "emote-gravity","61": "emote-judochop","62": "emote-jetpack","63": "emote-hugyourself",
            "64": "emote-hot","65": "emote-hero","66": "emote-hello","67": "emote-headball",
            "68": "emote-harlemshake","69": "emote-happy","70": "emote-handstand","71": "emote-greedy",
            "72": "emote-graceful","73": "emote-gordonshuffle","74": "emote-ghost-idle","75": "emote-gangnam",
            "76": "emote-frollicking","77": "emote-fainting","78": "emote-fail2","79": "emote-fail1",
            "80": "emote-exasperatedb","81": "emote-exasperated","82": "emote-elbowbump","83": "emote-disco",
            "84": "emote-disappear","85": "emote-deathdrop","86": "emote-death2","87": "emote-death",
            "88": "emote-dab","89": "emote-curtsy","90": "emote-confused","91": "emote-cold",
            "92": "emote-charging","93": "emote-bunnyhop","94": "emote-bow","95": "emote-boo",
            "96": "emote-baseball","97": "emote-apart","98": "emoji-thumbsup","99": "emoji-there",
            "100": "emoji-sneeze","101": "emoji-smirking","102": "emoji-sick","103": "emoji-scared",
            "104": "emoji-punch","105": "emoji-pray","106": "emoji-poop","107": "emoji-naughty",
            "108": "emoji-mind-blown","109": "emoji-lying","110": "emoji-halo","111": "emoji-hadoken",
            "112": "emoji-give-up","113": "emoji-gagging","114": "emoji-flex","115": "emoji-dizzy",
            "116": "emoji-cursing","117": "emoji-crying","118": "emoji-clapping","119": "emoji-celebrate",
            "120": "emoji-arrogance","121": "emoji-angry","122": "dance-voguehands","123": "dance-tiktok8",
            "124": "dance-tiktok2","125": "dance-spiritual","126": "dance-smoothwalk","127": "dance-singleladies",
            "128": "dance-shoppingcart","129": "dance-russian","130": "dance-robotic","131": "dance-pennywise",
            "132": "dance-orangejustice","133": "dance-metal","134": "dance-martial-artist","135": "dance-macarena",
            "136": "dance-handsup","137": "dance-duckwalk","138": "dance-breakdance","139": "dance-blackpink",
            "140": "dance-aerobics","141": "emote-hyped","142": "dance-jinglebell","143": "idle-nervous",
            "144": "idle-toilet","145": "emote-attention","146": "sit-open","147": "emote-astronaut",
            "148": "dance-zombie","149": "emoji-ghost","150": "emote-hearteyes","151": "emote-swordfight",
            "152": "emote-timejump","153": "emote-snake","154": "emote-heartfingers","155": "emote-heartshape",
            "156": "emote-hug","157": "emote-lagughing","158": "emoji-eyeroll","159": "emote-embarrassed",
            "160": "emote-float","161": "emote-telekinesis","162": "dance-sexy","163": "emote-puppet",
            "164": "idle-fighter","165": "dance-pinguin","166": "dance-creepypuppet","167": "emote-sleigh",
            "168": "emote-maniac","169": "emote-energyball","170": "idle_singing","171": "emote-frog",
            "172": "emote-superpose","173": "emote-cute","174": "dance-tiktok9","175": "dance-weird",
            "176": "dance-tiktok10","177": "emote-pose7","178": "emote-pose8","179": "idle-dance-casual",
            "180": "emote-pose1","181": "emote-pose3","182": "emote-pose5","183": "emote-cutey",
            "184": "emote-punkguitar","185": "emote-zombierun","186": "dance-jinglebell","187": "emote-gravity",
            "188": "dance-icecream","189": "dance-wrong","190": "idle-uwu","191": "idle-dance-tiktok4",
            "192": "emote-shy2","193": "dance-anime","194": "dance-kawai","195": "idle-wild",
            "196": "emote-iceskating","197": "emote-pose6","198": "emote-celebrationstep","199": "emote-creepycute",
            "200": "emote-frustrated","201": "emote-pose10","202": "sit-relaxed","203": "emote-stargaze",
            "204": "emote-slap","205": "emote-boxer","206": "emote-headblowup","207": "emote-kawaiigogo",
            "208": "emote-repose","209": "idle-dance-tiktok7","210": "emote-shrink","211": "emote-pose9",
            "212": "emote-teleporting","213": "dance-touch","214": "idle-guitar","215": "emote-gift",
            "216": "dance-employee","217": "emote-kissing","218": "dance-tiktok11","219": "emote-cutesalute",
            "220": "emote-salute","221": "idle-floorsleeping2","222": "dance-floss","223": "dance-tiktok11",
            "224": "dance-tiktok12","225": "dance-tiktok13","226": "emote-spiderman","227": "dance-breakdance",
            "228": "dance-twerk","229": "idle-space","230": "sit-idle-cute","231": "dance-true-heart",
            "232": "dance-griddy","233": "dance-ballet","234": "dance-freshprince","235": "emote-idle-daydreaming",
            "236": "emote-graceful","237": "dance-spiritual","238": "dance-popularvibe","239": "sit-idle-laidBack",
            "240": "dance-martial-artist","241": "dance-swagbounce","242": "emote-lust","243": "dance-woah",
            "244": "dance-mine","245": "emote-blowkisses","246": "emote-hero","247": "dance-shuffle",
            "248": "emote-knocking-screen","249": "emote-alice-shrink","250": "emote-threadexchange-star",
            "zombie": "idle_zombie","relaxed": "idle_layingdown2","attentive": "idle_layingdown",
            "sleepy": "idle-sleep","poutyFace": "idle-sad","posh": "idle-posh","tiredloop": "idle-loop-tired",
            "tapLoop": "idle-loop-tapdance","sit": "idle-loop-sitfloor","shy": "idle-loop-shy",
            "bummed": "idle-loop-sad","chillin'": "idle-loop-happy","annoyed": "idle-loop-annoyed",
            "aerobics": "idle-loop-aerobics","ponder": "idle-lookup","heropose": "idle-hero",
            "cozynap": "idle-floorsleeping","enthused": "idle-enthusiastic","boogieswing": "idle-dance-swinging",
            "feelthebeat": "idle-dance-headbobbing","irritated": "idle-angry","yes": "emote-yes",
            "ibelieveIcanfly": "emote-wings","theWave": "emote-wave","tired": "emote-tired",
            "think": "emote-think","theatrical": "emote-theatrical","tapdance": "emote-tapdance",
            "superrun": "emote-superrun","superPunch": "emote-superpunch","sumofight": "emote-sumo",
            "thumbSuck": "emote-suckthumb","splitsdrop": "emote-splitsdrop","snowballFight": "emote-snowball",
            "snowAngel": "emote-snowangel","shyemote": "emote-shy","secrehandshake": "emote-secrethandshake",
            "sad": "emote-sad","ropepull": "emote-ropepull","roll": "emote-roll","rofl": "emote-rofl",
            "robot": "emote-robot","rainbow": "emote-rainbow","proposing": "emote-proposing",
            "peekaboo": "emote-peekaboo","peace": "emote-peace","panic": "emote-panic","no": "emote-no",
            "ninjarun": "emote-ninjarun","nightfever": "emote-nightfever","monsterfail": "emote-monster_fail",
            "model": "emote-model","flirtywave": "emote-lust","levelUp": "emote-levelup",
            "amused": "emote-laughing2","laugh": "emote-laughing","kiss": "emote-kiss",
            "superKick": "emote-kicking","jump": "emote-jumpb","gravity": "emote-gravity",
            "judochop": "emote-judochop","imaginaryjetpack": "emote-jetpack","hugyourself": "emote-hugyourself",
            "sweating": "emote-hot","heroentrance": "emote-hero","hello": "emote-hello",
            "headball": "emote-headball","harlemShake": "emote-harlemshake","happy": "emote-happy",
            "handstand": "emote-handstand","greedyEmote": "emote-greedy","graceful": "emote-graceful",
            "moonwalk": "emote-gordonshuffle","ghostfloat": "emote-ghost-idle","gangnamstyle": "emote-gangnam",
            "frolic": "emote-frollicking","faint": "emote-fainting","clumsy": "emote-fail2",
            "fall": "emote-fail1","facePalm": "emote-exasperatedb","exasperated": "emote-exasperated",
            "elbowBump": "emote-elbowbump","disco": "emote-disco","blastOff": "emote-disappear",
            "faintDrop": "emote-deathdrop","collapse": "emote-death2","revival": "emote-death",
            "dab": "emote-dab","curtsy": "emote-curtsy","confusion": "emote-confused","cold": "emote-cold",
            "charging": "emote-charging","bunnyHop": "emote-bunnyhop","bow": "emote-bow","boo": "emote-boo",
            "homerun": "emote-baseball","fallingapart": "emote-apart","thumbsup": "emoji-thumbsup",
            "point": "emoji-there","sneeze": "emoji-sneeze","smirk": "emoji-smirking","sick": "emoji-sick",
            "gasp": "emoji-scared","punch": "emoji-punch","pray": "emoji-pray","stinky": "emoji-poop",
            "naughty": "emoji-naughty","mindBlown": "emoji-mind-blown","lying": "emoji-lying",
            "levitate": "emoji-halo","fireball Lunge": "emoji-hadoken","giveup": "emoji-give-up",
            "tummy Ache": "emoji-gagging","flex": "emoji-flex","stunned": "emoji-dizzy",
            "cursing Emote": "emoji-cursing","sob": "emoji-crying","clap": "emoji-clapping",
            "raiseTheRoof": "emoji-celebrate","arrogance": "emoji-arrogance","angry": "emoji-angry",
            "VogueHands": "dance-voguehands","SavageDance": "dance-tiktok8","DontStartNow": "dance-tiktok2",
            "YogaFlow": "dance-spiritual","Smoothwalk": "dance-smoothwalk","RingonIt": "dance-singleladies",
            "Let's Go Shopping": "dance-shoppingcart","russian Dance": "dance-russian","tobotic": "dance-robotic",
            "penny's Dance": "dance-pennywise","orange Juice Dance": "dance-orangejustice","rockout": "dance-metal",
            "karate": "dance-martial-artist","macarena": "dance-macarena","handsintheair": "dance-handsup",
            "duckealk": "dance-duckwalk","Breakdance": "dance-breakdance","kpop": "dance-blackpink",
            "PushUps": "dance-aerobics","Hyped": "emote-hyped","Jinglebell": "dance-jinglebell",
            "Nervous": "idle-nervous","Toilet": "idle-toilet","Attention": "emote-attention",
            "laidback": "sit-open","Astronaut": "emote-astronaut","DanceZombie": "dance-zombie",
            "ghost": "emoji-ghost","HeartEyes": "emote-hearteyes","Swordfight": "emote-swordfight",
            "TimeJump": "emote-timejump","Snake": "emote-snake","HeartFingers": "emote-heartfingers",
            "Heart Shape": "emote-heartshape","hug": "emote-hug","Laugh": "emote-lagughing",
            "Eyeroll": "emoji-eyeroll","Embarrassed": "emote-embarrassed","float": "emote-float",
            "Telekinesis": "emote-telekinesis","Sexydance": "dance-sexy","Puppet": "emote-puppet",
            "Fighter idle": "idle-fighter","Penguindance": "dance-pinguin","Creepypuppet": "dance-creepypuppet",
            "Sleigh": "emote-sleigh","Maniac": "emote-maniac","EnergyBall": "emote-energyball",
            "Singing": "idle_singing","Frog": "emote-frog","Superpose": "emote-superpose","Cute": "emote-cute",
            "TikTok9": "dance-tiktok9","Weird": "dance-weird","TikTok10": "dance-tiktok10",
            "pose7": "emote-pose7","pose8": "emote-pose8","casualDance": "idle-dance-casual",
            "pose1": "emote-pose1","pose3": "emote-pose3","pose5": "emote-pose5","Cutey": "emote-cutey",
            "PunkGuitar": "emote-punkguitar","zombieru": "emote-zombierun","fashionista": "dance-jinglebell",
            "icecream": "dance-icecream","wrong": "dance-wrong","uwu": "idle-uwu","TikTok4": "idle-dance-tiktok4",
            "advancedshy": "emote-shy2","anime": "dance-anime","kawaii": "dance-kawai","Scritchy": "idle-wild",
            "iceskating": "emote-iceskating","surpriseBig": "emote-pose6","celebrationStep": "emote-celebrationstep",
            "creepycute": "emote-creepycute","frustrated": "emote-frustrated","pose10": "emote-pose10",
            "relaxedsit": "sit-relaxed","stargazing": "emote-stargaze","slap": "emote-slap",
            "boxer": "emote-boxer","headBlowup": "emote-headblowup","kawaiiGoGo": "emote-kawaiigogo",
            "repose": "emote-repose","tiktok7": "idle-dance-tiktok7","shrink": "emote-shrink",
            "ditzyPose": "emote-pose9","teleporting": "emote-teleporting","touch": "dance-touch",
            "airuitar": "idle-guitar","thisIs For You": "emote-gift","pushit": "dance-employee",
            "sweetSmooch": "emote-kissing","tiktok11": "dance-tiktok11","cutesalute": "emote-cutesalute",
            "relaxing": "idle-floorsleeping2","attention": "emote-salute","floss": "dance-floss",
            "rest": "sit-idle-cute","aliceshrink": "emote-alice-shrink","threadexchangestar": "emote-threadexchange-star"
        }

        self.emote_durations = {
            "idle_zombie": 28.754937,"idle_layingdown2": 21.546653,"idle_layingdown": 24.585168,
            "idle-sleep": 22.620446,"idle-sad": 24.377214,"idle-posh": 21.851256,"idle-loop-tired": 21.959007,
            "idle-loop-tapdance": 6.261593,"idle-loop-sitfloor": 22.321055,"idle-loop-shy": 16.47449,
            "idle-loop-sad": 6.052999,"idle-loop-happy": 18.798322,"idle-loop-annoyed": 17.058522,
            "idle-loop-aerobics": 8.507535,"idle-lookup": 22.339865,"idle-hero": 21.877099,
            "idle-floorsleeping": 13.935264,"idle-enthusiastic": 15.941537,"idle-dance-swinging": 13.198551,
            "idle-dance-headbobbing": 25.367458,"idle-angry": 25.427848,"emote-yes": 2.565001,
            "emote-wings": 13.134487,"emote-wave": 2.690873,"emote-tired": 4.61063,"emote-think": 3.691104,
            "emote-theatrical": 8.591869,"emote-tapdance": 11.057294,"emote-superrun": 6.273226,
            "emote-superpunch": 3.751054,"emote-sumo": 10.868834,"emote-suckthumb": 4.185944,
            "emote-splitsdrop": 4.46931,"emote-snowball": 5.230467,"emote-snowangel": 6.218627,
            "emote-shy": 4.477567,"emote-secrethandshake": 3.879024,"emote-sad": 5.411073,
            "emote-ropepull": 8.769656,"emote-roll": 3.560517,"emote-rofl": 6.314731,"emote-robot": 7.607362,
            "emote-rainbow": 2.813373,"emote-proposing": 4.27888,"emote-peekaboo": 3.629867,
            "emote-peace": 5.755004,"emote-panic": 2.850966,"emote-no": 2.703034,"emote-ninjarun": 4.754721,
        }
        for k in ["emote-nightfever","emote-monster_fail","emote-model","emote-lust","emote-levelup",
            "emote-laughing2","emote-laughing","emote-kiss","emote-kicking","emote-jumpb","emote-gravity",
            "emote-judochop","emote-jetpack","emote-hugyourself","emote-hot","emote-hero","emote-hello",
            "emote-headball","emote-harlemshake","emote-happy","emote-handstand","emote-greedy",
            "emote-graceful","emote-gordonshuffle","emote-ghost-idle","emote-gangnam","emote-frollicking",
            "emote-fainting","emote-fail2","emote-fail1","emote-exasperatedb","emote-exasperated",
            "emote-elbowbump","emote-disco","emote-disappear","emote-deathdrop","emote-death2","emote-death",
            "emote-dab","emote-curtsy","emote-confused","emote-cold","emote-charging","emote-bunnyhop",
            "emote-bow","emote-boo","emote-baseball","emote-apart","emoji-thumbsup","emoji-there",
            "emoji-sneeze","emoji-smirking","emoji-sick","emoji-scared","emoji-punch","emoji-pray",
            "emoji-poop","emoji-naughty","emoji-mind-blown","emoji-lying","emoji-halo","emoji-hadoken",
            "emoji-give-up","emoji-gagging","emoji-flex","emoji-dizzy","emoji-cursing","emoji-crying",
            "emoji-clapping","emoji-celebrate","emoji-arrogance","emoji-angry","dance-voguehands",
            "dance-tiktok8","dance-tiktok2","dance-spiritual","dance-smoothwalk","dance-singleladies",
            "dance-shoppingcart","dance-russian","dance-robotic","dance-pennywise","dance-orangejustice",
            "dance-metal","dance-martial-artist","dance-macarena","dance-handsup","dance-duckwalk",
            "dance-breakdance","dance-blackpink","dance-aerobics","emote-hyped","dance-jinglebell",
            "idle-nervous","idle-toilet","emote-attention","sit-open","emote-astronaut","dance-zombie",
            "emoji-ghost","emote-hearteyes","emote-swordfight","emote-timejump","emote-snake",
            "emote-heartfingers","emote-heartshape","emote-hug","emote-lagughing","emoji-eyeroll",
            "emote-embarrassed","emote-float","emote-telekinesis","dance-sexy","emote-puppet","idle-fighter",
            "dance-pinguin","dance-creepypuppet","emote-sleigh","emote-maniac","emote-energyball",
            "idle_singing","emote-frog","emote-superpose","emote-cute","dance-tiktok9","dance-weird",
            "dance-tiktok10","emote-pose7","emote-pose8","idle-dance-casual","emote-pose1","emote-pose3",
            "emote-pose5","emote-cutey","emote-punkguitar","emote-zombierun","dance-icecream","dance-wrong",
            "idle-uwu","idle-dance-tiktok4","emote-shy2","dance-anime","dance-kawai","idle-wild",
            "emote-iceskating","emote-pose6","emote-celebrationstep","emote-creepycute","emote-frustrated",
            "emote-pose10","sit-relaxed","emote-stargaze","emote-slap","emote-boxer","emote-headblowup",
            "emote-kawaiigogo","emote-repose","idle-dance-tiktok7","emote-shrink","emote-pose9",
            "emote-teleporting","dance-touch","idle-guitar","emote-gift","dance-employee","emote-kissing",
            "dance-tiktok11","dance-tiktok12","dance-tiktok13","emote-cutesalute","emote-salute",
            "idle-floorsleeping2","dance-floss","emote-dead","emote-alice-shrink","emote-threadexchange-star",
            "sit-idle-cute","dance-true-heart","dance-griddy","dance-ballet","dance-freshprince",
            "emote-idle-daydreaming","dance-popularvibe","sit-idle-laidBack","dance-swagbounce","dance-woah",
            "dance-mine","emote-blowkisses","dance-shuffle","emote-knocking-screen","emote-spiderman",
            "dance-twerk","idle-space"]:
            self.emote_durations[k] = 15.0

    # ══════════════════════════════════════════════════
    #   سیستم چند زبانه
    # ══════════════════════════════════════════════════
    ALL_MESSAGES = {
        "fa": {
            "welcome": None,  # از config خوانده می‌شود
            "invalid_command": "❌ دستور نامعلوم! برای دیدن دستورات بات !help استفاده کنید یا به @luci.6969 پیام بدید.",
            "no_permission": "فقط ادمین‌ها می‌توانند از این دستور استفاده کنند!",
            "user_not_found": "کاربر {username} آنلاین نیست.",
            "invalid_format": "فرمت نادرست: {format}",
            "teleport_success": "@{username} به {location} تلپورت شد!",
            "teleport_error": "خطا در تلپورت: {error}",
            "heart_success": "{count} قلب بنفش به @{username} ارسال شد!",
            "heart_all_success": "{count} واکنش به {count} نفر ارسال شد!",
            "clap_success": "{count} clap به @{username} ارسال شد!",
            "wink_success": "{count} wink به @{username} ارسال شد!",
            "wave_success": "{count} wave به @{username} ارسال شد!",
            "thumbs_success": "{count} thumbs-up به @{username} ارسال شد!",
            "wallet_error": "خطا در دریافت موجودی: {error}",
            "tip_success": "{amount} گلد به @{username} ارسال شد.",
            "tip_all_success": "تیپ {amount} گلد به {count} نفر ارسال شد!",
            "ban_success": "@{username} بن شد!",
            "unban_success": "کاربر @{username} با موفقیت آنبن شد!",
            "unban_not_banned": "کاربر @{username} در لیست بن نیست.",
            "dancechain_success": "زنجیره رقص برای @{username} اجرا شد!",
            "addtele_success": "مکان {location} ذخیره شد!",
            "deltele_success": "مکان {location} با موفقیت حذف شد!",
            "deltele_not_found": "مکان {location} وجود ندارد!",
            "deltele_protected": "نمی‌توانید مکان پیش‌فرض {location} را حذف کنید!",
            "set_item_success": "ظاهر ربات به ایتم‌های @{username} تغییر کرد!",
            "listadd_empty": "هیچ ادمینی در لیست وجود ندارد.",
            "listadd_success": "لیست ادمین‌ها ({count} نفر):\n{admin_list}",
            "freeze_success": "کاربر @{username} فریز شد!",
            "unfreeze_success": "کاربر @{username} از حالت فریز آزاد شد!",
            "unfreeze_not_frozen": "کاربر @{username} فریز نشده است!",
            "party_success": "رقص شماره {dance_number} برای @{username} فعال شد!",
            "party_all_success": "رقص شماره {dance_number} برای {count} کاربر فعال شد!",
            "partys_success": "رقص اجباری برای @{username} متوقف شد!",
            "partys_not_dancing": "کاربر @{username} در حال رقص اجباری نیست!",
            "lang_changed": "زبان ربات به فارسی تغییر کرد! 🇮🇷",
            "lang_invalid": "زبان نامعتبر! از !lang fa یا !lang tr یا !lang en استفاده کنید.",
            "lang_no_permission": "فقط ادمین‌ها می‌توانند زبان را تغییر دهند!",
        },
        "tr": {
            "welcome": "Hoş geldiniz! :Bot yapımcısı: @luci.6969",
            "invalid_command": "❌ Bilinmeyen komut! Komutları görmek için !help kullanın veya @luci.6969 mesaj atın.",
            "no_permission": "Bu komutu sadece adminler kullanabilir!",
            "user_not_found": "{username} kullanıcısı çevrimiçi değil.",
            "invalid_format": "Yanlış format: {format}",
            "teleport_success": "@{username} kullanıcısı {location} konumuna ışınlandı!",
            "teleport_error": "Işınlanma hatası: {error}",
            "heart_success": "@{username} kullanıcısına {count} kalp gönderildi!",
            "heart_all_success": "{count} kişiye {count} tepki gönderildi!",
            "clap_success": "@{username} kullanıcısına {count} alkış gönderildi!",
            "wink_success": "@{username} kullanıcısına {count} göz kırpma gönderildi!",
            "wave_success": "@{username} kullanıcısına {count} el sallama gönderildi!",
            "thumbs_success": "@{username} kullanıcısına {count} beğeni gönderildi!",
            "wallet_error": "Bakiye alınırken hata oluştu: {error}",
            "tip_success": "@{username} kullanıcısına {amount} altın gönderildi.",
            "tip_all_success": "{count} kişiye {amount} altın bahşiş gönderildi!",
            "ban_success": "@{username} yasaklandı!",
            "unban_success": "@{username} kullanıcısının yasağı başarıyla kaldırıldı!",
            "unban_not_banned": "@{username} kullanıcısı yasaklı listesinde değil.",
            "dancechain_success": "@{username} için dans zinciri çalıştırıldı!",
            "addtele_success": "{location} konumu kaydedildi!",
            "deltele_success": "{location} konumu başarıyla silindi!",
            "deltele_not_found": "{location} konumu bulunamadı!",
            "deltele_protected": "Varsayılan {location} konumunu silemezsiniz!",
            "set_item_success": "Botun görünümü @{username} kullanıcısının kıyafetlerine değiştirildi!",
            "listadd_empty": "Listede hiç admin yok.",
            "listadd_success": "Admin listesi ({count} kişi):\n{admin_list}",
            "freeze_success": "@{username} kullanıcısı donduruldu!",
            "unfreeze_success": "@{username} kullanıcısı çözüldü!",
            "unfreeze_not_frozen": "@{username} kullanıcısı zaten dondurulmamış!",
            "party_success": "{dance_number} numaralı dans @{username} için başlatıldı!",
            "party_all_success": "{dance_number} numaralı dans {count} kullanıcı için başlatıldı!",
            "partys_success": "@{username} için zorunlu dans durduruldu!",
            "partys_not_dancing": "@{username} kullanıcısı zorunlu dansta değil!",
            "lang_changed": "Bot dili Türkçe olarak değiştirildi! 🇹🇷",
            "lang_invalid": "Geçersiz dil! !lang fa veya !lang tr veya !lang en kullanın.",
            "lang_no_permission": "Dili sadece adminler değiştirebilir!",
        },
        "en": {
            "welcome": "Welcome! :Bot creator: @luci.6969",
            "invalid_command": "❌ Unknown command! Use !help to see commands or message @luci.6969.",
            "no_permission": "Only admins can use this command!",
            "user_not_found": "User {username} is not online.",
            "invalid_format": "Invalid format: {format}",
            "teleport_success": "@{username} was teleported to {location}!",
            "teleport_error": "Teleport error: {error}",
            "heart_success": "Sent {count} hearts to @{username}!",
            "heart_all_success": "Sent {count} reactions to {count} users!",
            "clap_success": "Sent {count} claps to @{username}!",
            "wink_success": "Sent {count} winks to @{username}!",
            "wave_success": "Sent {count} waves to @{username}!",
            "thumbs_success": "Sent {count} thumbs-up to @{username}!",
            "wallet_error": "Error fetching wallet: {error}",
            "tip_success": "Sent {amount} gold to @{username}.",
            "tip_all_success": "Tipped {amount} gold to {count} users!",
            "ban_success": "@{username} has been banned!",
            "unban_success": "@{username} has been unbanned successfully!",
            "unban_not_banned": "@{username} is not in the ban list.",
            "dancechain_success": "Dance chain executed for @{username}!",
            "addtele_success": "Location {location} saved!",
            "deltele_success": "Location {location} deleted successfully!",
            "deltele_not_found": "Location {location} not found!",
            "deltele_protected": "You cannot delete the default location {location}!",
            "set_item_success": "Bot appearance changed to @{username}'s outfit!",
            "listadd_empty": "No admins in the list.",
            "listadd_success": "Admin list ({count} users):\n{admin_list}",
            "freeze_success": "@{username} has been frozen!",
            "unfreeze_success": "@{username} has been unfrozen!",
            "unfreeze_not_frozen": "@{username} is not frozen!",
            "party_success": "Dance #{dance_number} started for @{username}!",
            "party_all_success": "Dance #{dance_number} started for {count} users!",
            "partys_success": "Forced dance stopped for @{username}!",
            "partys_not_dancing": "@{username} is not in a forced dance!",
            "lang_changed": "Bot language changed to English! 🇬🇧",
            "lang_invalid": "Invalid language! Use !lang fa, !lang tr, or !lang en.",
            "lang_no_permission": "Only admins can change the language!",
        }
    }

    def is_host(self, username: str) -> bool:
        return username.lower() in [h.lower() for h in self.config.get("host_usernames", [])]

    def load_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key not in self.config:
                        self.config[key] = value.copy() if isinstance(value, (list, dict)) else value
                logger.info("تنظیمات با موفقیت بارگذاری شد.")
            else:
                logger.info("فایل تنظیمات یافت نشد، استفاده از تنظیمات پیش‌فرض...")
                self.config = DEFAULT_CONFIG
                self.save_config()
        except json.JSONDecodeError as e:
            logger.error(f"خطا در ساختار JSON فایل تنظیمات: {e}")
            self.config = DEFAULT_CONFIG
            self.save_config()
        except Exception as e:
            logger.error(f"خطا در بارگذاری تنظیمات: {e}")
            self.config = DEFAULT_CONFIG
            self.save_config()

        for host in self.config.get("host_usernames", []):
            if host not in self.config["admin_usernames"]:
                self.config["admin_usernames"].append(host)

    def save_config(self):
        try:
            config_to_save = self.config.copy()
            config_to_save["host_usernames"] = list(config_to_save["host_usernames"])
            config_to_save["admin_usernames"] = list(config_to_save["admin_usernames"])
            config_to_save["vip_usernames"] = list(config_to_save["vip_usernames"])
            config_to_save["banned_users"] = list(config_to_save["banned_users"])
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
            logger.info("تنظیمات با موفقیت ذخیره شد.")
        except Exception as e:
            logger.error(f"خطا در ذخیره تنظیمات: {e}")

    def get_message(self, key, **kwargs):
        lang = self.config.get("language", "fa")
        messages = self.ALL_MESSAGES.get(lang, self.ALL_MESSAGES["fa"])
        # welcome mesajı için config'den oku (fa'da), diğer dillerde ALL_MESSAGES'dan
        if key == "welcome":
            if lang == "fa":
                text = self.config.get("welcome_message", self.ALL_MESSAGES["fa"]["welcome"] or "خوش وامدی!")
            else:
                text = messages.get("welcome") or self.config.get("welcome_message", "Welcome!")
        else:
            text = messages.get(key, self.ALL_MESSAGES["fa"].get(key, key))
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    # ══════════════════════════════════════════════════
    #   !lang komutu
    # ══════════════════════════════════════════════════
    async def cmd_lang(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("lang_no_permission"))
            return
        if len(parts) < 2:
            await self.highrise.chat(self.get_message("lang_invalid"))
            return
        lang = parts[1].lower()
        if lang not in ("fa", "tr", "en"):
            await self.highrise.chat(self.get_message("lang_invalid"))
            return
        self.config["language"] = lang
        self.save_config()
        await self.highrise.chat(self.get_message("lang_changed"))
        logger.info(f"Dil {lang} olarak değiştirildi. Değiştiren: {user.username}")

    async def cleanup_tasks(self):
        try:
            for username, task in self.dance_tasks.items():
                if not task.done():
                    task.cancel()
                try:
                    await task
                except CancelledError:
                    pass
            self.dance_tasks.clear()
            self.user_dances.clear()
            self.party_dances.clear()
            for username, task in self.frozen_users.items():
                if not task.done():
                    task.cancel()
                try:
                    await task
                except CancelledError:
                    pass
            self.frozen_users.clear()
            if self.announcement_task and not self.announcement_task.done():
                self.announcement_task.cancel()
                try:
                    await self.announcement_task
                except CancelledError:
                    pass
                self.announcement_task = None
            if self.score_update_task and not self.score_update_task.done():
                self.score_update_task.cancel()
                try:
                    await self.score_update_task
                except CancelledError:
                    pass
                self.score_update_task = None
            logger.info("همه وظایف ناهمزمان لغو شدند.")
        except Exception as e:
            logger.error(f"خطا در لغو وظایف: {e}")

    async def on_start(self, session_metadata):
        logger.info("ربات با موفقیت وصل شد.")
        self.user_id = getattr(session_metadata, "user_id", None)
        if not self.user_id:
            logger.error("شناسه ربات در session_metadata پیدا نشد.")
            await self.highrise.chat("خطا: شناسه ربات پیدا نشد.")
            return
        try:
            dest = Position(x=16.5, y=0.25, z=3.5)
            await self.highrise.teleport(user_id=self.user_id, dest=dest)
            await self.highrise.chat("ربات به موقعیت اولیه (x=0.5, y=1.0, z=1.5) منتقل شد!")
            logger.info("ربات به موقعیت اولیه تلپورت شد.")
        except Exception as e:
            logger.error(f"خطا در تلپورت اولیه: {e}")
            await self.highrise.chat(f"خطا در تلپورت اولیه: {e}")
        await self.sync_room_users()
        self.announcement_task = create_task(self.announcement_loop())
        self.score_update_task = create_task(self.score_update_loop())

    async def on_user_join(self, user: User, position: Position):
        username = user.username.lower()
        if username in self.config["banned_users"]:
            try:
                await self.highrise.moderate_room(user.id, "kick")
                logger.info(f"کاربر بن‌شده {user.username} به صورت خودکار کیک شد.")
            except Exception as e:
                logger.error(f"خطا در کیک کردن {user.username}: {e}")
            return
        self.active_users[username] = user
        self.user_positions[username] = position
        self.user_scores[username] = self.user_scores.get(username, 0) + 10
        await self.highrise.chat(self.get_message("welcome", username=user.username))
        logger.info(f"کاربر {user.username} (ID: {user.id}) وارد روم شد. موقعیت: {position}")

    async def on_user_leave(self, user: User, position: Position | None = None):
        username = user.username.lower()
        self.active_users.pop(username, None)
        self.user_positions.pop(username, None)
        if username in self.dance_tasks:
            self.dance_tasks[username].cancel()
            self.dance_tasks.pop(username, None)
            self.user_dances.pop(username, None)
            self.party_dances.pop(username, None)
        if username in self.frozen_users:
            self.frozen_users[username].cancel()
            self.frozen_users.pop(username, None)
        await self.highrise.chat(f"@{user.username} از روم خارج شد.")
        logger.info(f"کاربر {user.username} (ID: {user.id}) از روم خارج شد. موقعیت: {position}")

    async def sync_room_users(self):
        try:
            room_users = await self.highrise.get_room_users()
            current_users = {user_data[0].username.lower(): user_data for user_data in room_users.content}
            for username in list(self.active_users.keys()):
                if username not in current_users:
                    self.active_users.pop(username, None)
                    self.user_positions.pop(username, None)
                    if username in self.dance_tasks:
                        self.dance_tasks[username].cancel()
                        self.dance_tasks.pop(username, None)
                    if username in self.frozen_users:
                        self.frozen_users[username].cancel()
                        self.frozen_users.pop(username, None)
                    logger.info(f"کاربر {username} از لیست‌ها حذف شد (همگام‌سازی).")
            for username, user_data in current_users.items():
                self.active_users[username] = user_data[0]
                self.user_positions[username] = user_data[1]
            logger.info(f"همگام‌سازی کاربران انجام شد. تعداد کاربران: {len(self.active_users)}.")
            await self.highrise.chat(f"{len(self.active_users)} کاربر در روم شناسایی شدند.")
        except Exception as e:
            logger.error(f"خطا در همگام‌سازی کاربران: {e}", exc_info=True)
            await self.highrise.chat("خطا در شناسایی کاربران روم.")

    async def announcement_loop(self):
        try:
            while True:
                await sleep(self.config["announcement_interval"])
                await self.highrise.chat(self.config["announcement_message"])
                logger.info("پیام اطلاع‌رسانی ارسال شد.")
        except CancelledError:
            logger.info("وظیفه اطلاع‌رسانی لغو شد.")
        except Exception as e:
            logger.error(f"خطا در حلقه اطلاع‌رسانی: {e}")

    async def score_update_loop(self):
        try:
            while True:
                await sleep(300)
                for username in self.active_users:
                    self.user_scores[username] = self.user_scores.get(username, 0) + 5
                logger.info("امتیازات کاربران به‌روزرسانی شد.")
        except CancelledError:
            logger.info("وظیفه به‌روزرسانی امتیازات لغو شد.")
        except Exception as e:
            logger.error(f"خطا در حلقه به‌روزرسانی امتیازات: {e}")

    async def on_user_move(self, user: User, position: Position):
        username = user.username.lower()
        self.user_positions[username] = position
        if username in self.frozen_users:
            try:
                original_position = self.user_positions.get(username)
                if original_position:
                    await self.highrise.teleport(user_id=user.id, dest=original_position)
            except Exception as e:
                logger.error(f"خطا در بازگرداندن {username} به موقعیت فریز: {e}")

    async def on_chat(self, user: User, message: str):
        username = user.username.lower()
        msg = message.strip()
        msg_lower = msg.lower()
        try:
            self.user_scores[username] = self.user_scores.get(username, 0) + 2
            if msg_lower in self.emotes:
                await self.start_dance(user, self.emotes[msg_lower])
            elif msg_lower in ["stop", "استوپ"]:
                await self.stop_dance(user)
            elif msg_lower in ["سازنده", "creature", "creator", "سازندت", "سازنده بات"]:
                await self.highrise.chat("👑 سازنده این بات: @luci.6969👑")
            elif msg_lower.startswith("!"):
                parts = msg.split()
                parts_lower = [p.lower() for p in parts]
                cmd = parts_lower[0] if len(parts_lower) == 1 else ("!item set" if parts_lower[0] == "!item" else parts_lower[0])
                if cmd in self.commands:
                    await self.commands[cmd](user, parts)
                else:
                    await self.highrise.chat(self.get_message("invalid_command"))
        except Exception as e:
            logger.error(f"خطا در on_chat از {username}: {e}")

    async def on_message(self, user_id: str, text: str, message_id: str) -> None:
        logger.info(f"📥 دایرکت مسیج جدید از کاربر [{user_id}]: {text}")
        if user_id == self.user_id:
            return
        auto_reply = (
            "سلام عزیز! ❤️\n\n"
            "🤖 من یک ربات پیشرفته و فول امکانات برای مدیریت و ارتقای روم هستم!\n\n"
            "✨ **بخشی از قابلیت‌های خفن من:**\n"
            "🔹 دارای ۲۴۸ دنس جذاب و فعال با تکرار همیشگی و بدون حتی ۱ ثانیه تاخیر! 💃\n"
            "🔹 سیستم خوش‌آمدگویی هوشمند و خودکار به محض ورود پلیرها 🚪\n"
            "🔹 قابلیت رقص همگانی و پارتی خودکار برای کل اعضای روم 🕺\n"
            "🔹 امنیت بالا و مدیریت کامل ادمین‌ها و دستورات اختصاصی 🛠️\n"
            "🔹 میزبانی ۲۴ ساعته و آنلاین بدون قطعی روی سرورهای قدرتمند ⚡\n\n"
            "🤝 **شرایط رنت (اجاره):**\n"
            "برای اجاره یا همان رنت این ربات فوق‌العاده برای روم خود، لطفاً همین الان به آیدی زیر پیام بدید:\n"
            "👉 @luci.6969 👈"
        )
        try:
            await self.highrise.send_message(user_id, auto_reply)
        except Exception as e:
            logger.error(f"خطا در ارسال پاسخ خودکار دایرکت: {e}")

    async def on_tip(self, sender: User, receiver: User, tip):
        try:
            amount = getattr(tip, "amount", 0)
            await self.highrise.chat(f"@{sender.username} {amount} گلد به @{receiver.username} داد!")
            self.user_scores[sender.username.lower()] = self.user_scores.get(sender.username.lower(), 0) + amount
            logger.info(f"کاربر {sender.username} {amount} گلد به {receiver.username} تیپ داد.")
        except Exception as e:
            logger.error(f"خطا در پردازش تیپ از {sender.username} به {receiver.username}: {e}")

    async def start_dance(self, user: User, emote: str):
        username = user.username.lower()
        await self.stop_dance(user)
        self.user_dances[username] = emote
        duration = self.emote_durations.get(emote, 15.0)
        sleep_time = duration + 1.0
        async def dance_loop():
            try:
                while self.user_dances.get(username) == emote:
                    await self.highrise.send_emote(emote, user.id)
                    await sleep(sleep_time)
            except CancelledError:
                logger.info(f"وظیفه رقص برای {username} لغو شد.")
            except Exception as e:
                logger.error(f"خطا در حلقه رقص برای {username}: {e}")
        task = create_task(dance_loop())
        self.dance_tasks[username] = task
        logger.info(f"کاربر {username} شروع به رقص {emote} کرد.")

    async def stop_dance(self, user: User):
        username = user.username.lower()
        if username in self.party_dances and self.party_dances[username][1]:
            await self.highrise.chat(f"@{username} نمی‌توانید رقص اجباری را متوقف کنید! فقط ادمین با !partys می‌تواند آن را متوقف کند.")
            return
        if username in self.dance_tasks:
            self.user_dances.pop(username, None)
            self.party_dances.pop(username, None)
            self.dance_tasks[username].cancel()
            self.dance_tasks.pop(username, None)

    async def cmd_help(self, user: User, parts: list):
        lang = self.config.get("language", "fa")
        if lang == "tr":
            help_text = (
                "Bot komutları:\n"
                "1-250 - Dans yap\nstop - Dansı durdur\n!help - Yardım\n"
                "!spam sayı mesaj - Spam\n!tele @kullanıcı [konum] - Işınla\n"
                "!heart sayı @kullanıcı - Kalp\n!clap sayı @kullanıcı - Alkış\n"
                "!wink sayı @kullanıcı - Göz kırp\n!wave sayı @kullanıcı - El salla\n"
                "!thumbs sayı @kullanıcı - Beğeni\n!wallet - Bakiye\n!set - Bota gel\n"
                "!tip miktar all - Bahşiş\n!vip - VIP konumu\n!dj - DJ konumu\n"
                "!ban @kullanıcı - Yasakla\n!unban @kullanıcı - Yasak kaldır\n"
                "!freeze @kullanıcı - Dondur\n!unfreeze @kullanıcı - Çöz\n"
                "!party @kullanıcı sayı - Zorla dans\n!partys @kullanıcı - Dansı durdur\n"
                "!emotebot dans - Bot dansı\n!loopchat mesaj - Tekrar mesaj\n"
                "!lang fa/tr/en - Dil değiştir\n"
                "📩 Bilgi için @luci.6969 mesaj at!"
            )
        elif lang == "en":
            help_text = (
                "Bot commands:\n"
                "1-250 - Dance\nstop - Stop dance\n!help - Help\n"
                "!spam count message - Spam\n!tele @user [location] - Teleport\n"
                "!heart count @user - Hearts\n!clap count @user - Clap\n"
                "!wink count @user - Wink\n!wave count @user - Wave\n"
                "!thumbs count @user - Thumbs up\n!wallet - Wallet\n!set - Come to bot\n"
                "!tip amount all - Tip all\n!vip - VIP location\n!dj - DJ location\n"
                "!ban @user - Ban\n!unban @user - Unban\n"
                "!freeze @user - Freeze\n!unfreeze @user - Unfreeze\n"
                "!party @user num - Force dance\n!partys @user - Stop dance\n"
                "!emotebot dance - Bot emote\n!loopchat message - Loop message\n"
                "!lang fa/tr/en - Change language\n"
                "📩 Info: message @luci.6969!"
            )
        else:
            help_text = (
                "دستورات ربات:\n1-250 - اجرای رقص\nstop - توقف رقص\n!help - راهنما\n"
                "!spam تعداد پیام - اسپم\n!tele @username [مکان] - تلپورت\n"
                "!heart تعداد @username - قلب\n!clap تعداد @username - clap\n"
                "!wink تعداد @username - wink\n!wave تعداد @username - wave\n"
                "!thumbs تعداد @username - thumbs-up\n!wallet - موجودی\n!set - تلپورت ربات\n"
                "!tip مقدار all - تیپ\n!vip - تلپورت VIP\n!dj - تلپورت DJ\n"
                "!ban @username - بن\n!unban @username - آنبن\n"
                "!freeze @username - فریز\n!unfreeze @username - آنفریز\n"
                "!party @username عدد - رقص اجباری\n!partys @username - توقف رقص\n"
                "!emotebot دنس - دنس ربات\n!loopchat پیام - پیام تکرار\n"
                "!lang fa/tr/en - تغییر زبان\n"
                "📩 اطلاعات بیشتر: @luci.6969"
            )
        for chunk in [help_text[i:i+200] for i in range(0, len(help_text), 200)]:
            await self.highrise.chat(chunk)
        logger.info(f"راهنما توسط {user.username} درخواست شد.")

    async def cmd_spam(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) < 2 or not parts[1].isdigit():
            await self.highrise.chat(self.get_message("invalid_format", format="!spam تعداد پیام"))
            return
        try:
            count = int(parts[1])
            spam_message = " ".join(parts[2:]) if len(parts) > 2 else "اسپم آزمایشی!"
            if count < 1 or count > 100:
                await self.highrise.chat("تعداد پیام‌ها باید بین 1 تا 100 باشد.")
                return
            for _ in range(count):
                await self.highrise.chat(spam_message)
                await sleep(2.0)
            await self.highrise.chat(f"{count} پیام اسپم ارسال شد!")
        except Exception as e:
            await self.highrise.chat(f"خطا در ارسال پیام اسپم: {str(e)}")

    async def cmd_tele(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) == 3 and parts[1].startswith("@"):
            target_username = parts[1][1:].lower()
            location = parts[2]
            target_user = self.active_users.get(target_username)
            if not target_user:
                await self.highrise.chat(self.get_message("user_not_found", username=target_username))
                return
            if location not in self.config["teleport_locations"]:
                await self.highrise.chat(f"مکان {location} وجود ندارد!")
                return
            try:
                dest_data = self.config["teleport_locations"][location]
                dest = Position(x=dest_data["x"], y=dest_data["y"], z=dest_data["z"])
                await self.highrise.teleport(user_id=target_user.id, dest=dest)
                await self.highrise.chat(self.get_message("teleport_success", username=target_user.username, location=location.upper()))
            except Exception as e:
                await self.highrise.chat(self.get_message("teleport_error", error=str(e)))
        elif len(parts) == 3 and parts[1] == "to" and parts[2].startswith("@"):
            target_username = parts[2][1:].lower()
            target_user = self.active_users.get(target_username)
            if not target_user:
                await self.highrise.chat(self.get_message("user_not_found", username=target_username))
                return
            try:
                position = self.user_positions.get(target_username)
                if position:
                    await self.highrise.teleport(user_id=user.id, dest=position)
                    await self.highrise.chat(f"@{user.username} به مکان @{target_user.username} تلپورت شد.")
            except Exception as e:
                await self.highrise.chat(self.get_message("teleport_error", error=str(e)))
        elif len(parts) == 3 and parts[1] == "me" and parts[2].startswith("@"):
            target_username = parts[2][1:].lower()
            target_user = self.active_users.get(target_username)
            if not target_user:
                await self.highrise.chat(self.get_message("user_not_found", username=target_username))
                return
            try:
                position = self.user_positions.get(user.username.lower())
                if position:
                    await self.highrise.teleport(user_id=target_user.id, dest=position)
                    await self.highrise.chat(f"@{target_user.username} به مکان @{user.username} تلپورت شد.")
            except Exception as e:
                await self.highrise.chat(self.get_message("teleport_error", error=str(e)))
        elif len(parts) == 3 and parts[1] == "me" and parts[2] == "all":
            admin_position = self.user_positions.get(user.username.lower())
            if not admin_position:
                await self.highrise.chat("موقعیت شما در دسترس نیست.")
                return
            try:
                successful_teleports = 0
                for username, target_user in self.active_users.items():
                    if target_user.id == user.id or target_user.id == self.user_id:
                        continue
                    try:
                        await self.highrise.teleport(user_id=target_user.id, dest=admin_position)
                        successful_teleports += 1
                        await sleep(0.5)
                    except Exception as e:
                        logger.error(f"خطا در تلپورت {username}: {e}")
                await self.highrise.chat(f"{successful_teleports} کاربر به مکان @{user.username} تلپورت شدند.")
            except Exception as e:
                await self.highrise.chat(self.get_message("teleport_error", error=str(e)))
        else:
            await self.highrise.chat(self.get_message("invalid_format", format="!tele @username [مکان] یا !tele to @username یا !tele me @username یا !tele me all"))

    async def _react_to(self, user, parts, reaction_id, success_key, all_key):
        parts = [p.lower() for p in parts]
        if len(parts) == 2 and parts[1] == "all":
            if user.username.lower() not in self.config["admin_usernames"]:
                await self.highrise.chat(self.get_message("no_permission"))
                return
            active = list(self.active_users.items())
            count = 0
            for uname, tu in active:
                if tu.id == self.user_id:
                    continue
                try:
                    await self.highrise.react(reaction_id, tu.id)
                    count += 1
                    await sleep(0.5)
                except Exception as e:
                    logger.error(f"react error: {e}")
            await self.highrise.chat(self.get_message("heart_all_success", count=count))
            return
        if len(parts) != 3:
            await self.highrise.chat(self.get_message("invalid_format", format=f"!{reaction_id} تعداد @username یا !{reaction_id} all"))
            return
        try:
            count = int(parts[1])
        except ValueError:
            await self.highrise.chat(f"@{user.username}: عدد نامعتبر است.")
            return
        target_username = parts[2].lstrip('@').lower()
        target_user = next((u for u in self.active_users.values() if u.username.lower() == target_username), None)
        if not target_user:
            await self.highrise.chat(self.get_message("user_not_found", username=target_username))
            return
        for _ in range(count):
            await self.highrise.react(reaction_id, target_user.id)
            await sleep(0.5)
        await self.highrise.chat(self.get_message(success_key, count=count, username=target_user.username))

    async def cmd_heart(self, user, parts): await self._react_to(user, parts, "heart", "heart_success", "heart_all_success")
    async def cmd_clap(self, user, parts): await self._react_to(user, parts, "clap", "clap_success", "heart_all_success")
    async def cmd_wink(self, user, parts): await self._react_to(user, parts, "wink", "wink_success", "heart_all_success")
    async def cmd_wave(self, user, parts): await self._react_to(user, parts, "wave", "wave_success", "heart_all_success")
    async def cmd_thumbs(self, user, parts): await self._react_to(user, parts, "thumbs-up", "thumbs_success", "heart_all_success")

    async def cmd_wallet(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        try:
            wallet = await self.highrise.get_wallet()
            gold_amount = 0
            if hasattr(wallet, "content") and isinstance(wallet.content, list):
                for item in wallet.content:
                    if hasattr(item, "type") and item.type == "gold" and hasattr(item, "amount"):
                        gold_amount = item.amount
                        break
            await self.highrise.chat(f"موجودی گلد ربات: {gold_amount} گلد")
        except Exception as e:
            await self.highrise.chat(self.get_message("wallet_error", error=str(e)))

    async def cmd_tip(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 3 or not parts[1].isdigit() or parts[2] != "all":
            await self.highrise.chat(self.get_message("invalid_format", format="!tip <تعداد> all (تعداد: 1، 5، 10، 50، 100)"))
            return
        try:
            tip_amount = int(parts[1])
            if tip_amount not in [1, 5, 10, 50, 100]:
                await self.highrise.chat("مقدار گلد باید 1، 5، 10، 50 یا 100 باشد.")
                return
            gold_bar_map = {1: "gold_bar_1", 5: "gold_bar_5", 10: "gold_bar_10", 50: "gold_bar_50", 100: "gold_bar_100"}
            gold_bar_item = gold_bar_map.get(tip_amount)
            active_users = [u for u in self.active_users.values() if u.id != self.user_id]
            successful_tips = 0
            for target_user in active_users:
                try:
                    await self.highrise.tip_user(target_user.id, gold_bar_item)
                    successful_tips += 1
                    await self.highrise.chat(self.get_message("tip_success", amount=tip_amount, username=target_user.username))
                    await sleep(3.0)
                except Exception as e:
                    logger.error(f"tip error for {target_user.username}: {e}")
            if successful_tips > 0:
                await self.highrise.chat(self.get_message("tip_all_success", amount=tip_amount, count=successful_tips))
        except Exception as e:
            await self.highrise.chat(f"خطای ناشناخته: {e}")

    async def cmd_set(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        pos = self.user_positions.get(user.username.lower())
        if not pos:
            await self.highrise.chat(f"@{user.username}: موقعیت شما مشخص نیست.")
            return
        try:
            await self.highrise.teleport(user_id=self.user_id, dest=pos)
            await self.highrise.chat(f"ربات به موقعیت @{user.username} منتقل شد.")
        except Exception as e:
            await self.highrise.chat(f"خطا در تلپورت ربات: {e}")

    async def cmd_vip(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        try:
            dest_data = self.config["teleport_locations"]["vip"]
            dest = Position(x=dest_data["x"], y=dest_data["y"], z=dest_data["z"])
            await self.highrise.teleport(user_id=user.id, dest=dest)
            await self.highrise.chat(self.get_message("teleport_success", username=user.username, location="VIP"))
        except Exception as e:
            await self.highrise.chat(self.get_message("teleport_error", error=str(e)))

    async def cmd_vip1(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        try:
            dest_data = self.config["teleport_locations"]["vip1"]
            dest = Position(x=dest_data["x"], y=dest_data["y"], z=dest_data["z"])
            await self.highrise.teleport(user_id=user.id, dest=dest)
            await self.highrise.chat(self.get_message("teleport_success", username=user.username, location="VIP1"))
        except Exception as e:
            await self.highrise.chat(self.get_message("teleport_error", error=str(e)))

    async def cmd_dj(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        try:
            dest_data = self.config["teleport_locations"]["dj"]
            dest = Position(x=dest_data["x"], y=dest_data["y"], z=dest_data["z"])
            await self.highrise.teleport(user_id=user.id, dest=dest)
            await self.highrise.chat(self.get_message("teleport_success", username=user.username, location="DJ"))
        except Exception as e:
            await self.highrise.chat(self.get_message("teleport_error", error=str(e)))

    async def cmd_down(self, user: User, parts: list):
        try:
            dest = Position(x=2.0, y=0.5, z=1.5)
            await self.highrise.teleport(user_id=user.id, dest=dest)
            await self.highrise.chat(f"@{user.username} به پایین رفت.")
        except Exception as e:
            await self.highrise.chat(self.get_message("teleport_error", error=str(e)))

    async def cmd_ban(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!ban @username"))
            return
        target_username = parts[1][1:].lower()
        target_user = self.active_users.get(target_username)
        if not target_user:
            await self.highrise.chat(self.get_message("user_not_found", username=target_username))
            return
        self.config["banned_users"].append(target_username)
        self.save_config()
        await self.highrise.chat(self.get_message("ban_success", username=target_username))

    async def cmd_unban(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!unban @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username not in self.config["banned_users"]:
            await self.highrise.chat(self.get_message("unban_not_banned", username=target_username))
            return
        self.config["banned_users"].remove(target_username)
        self.save_config()
        await self.highrise.chat(self.get_message("unban_success", username=target_username))

    async def cmd_dancechain(self, user: User, parts: list):
        dance_list = ["dance-tiktok8", "dance-blackpink", "dance-tiktok2"]
        for emote in dance_list:
            await self.highrise.send_emote(emote, user.id)
            await sleep(self.emote_durations.get(emote, 15.0))
        await self.highrise.chat(self.get_message("dancechain_success", username=user.username))

    async def cmd_addtele(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2:
            await self.highrise.chat(self.get_message("invalid_format", format="!addtele نام_مکان"))
            return
        location_name = parts[1]
        pos = self.user_positions.get(user.username.lower())
        if not pos:
            await self.highrise.chat("موقعیت شما مشخص نیست!")
            return
        self.config["teleport_locations"][location_name] = {"x": pos.x, "y": pos.y, "z": pos.z}
        self.save_config()
        await self.highrise.chat(self.get_message("addtele_success", location=location_name))

    async def cmd_deltele(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2:
            await self.highrise.chat(self.get_message("invalid_format", format="!deltele نام_مکان"))
            return
        location_name = parts[1]
        if location_name in ["vip", "vip1", "dj"]:
            await self.highrise.chat(self.get_message("deltele_protected", location=location_name))
            return
        if location_name not in self.config["teleport_locations"]:
            await self.highrise.chat(self.get_message("deltele_not_found", location=location_name))
            return
        del self.config["teleport_locations"][location_name]
        self.save_config()
        await self.highrise.chat(self.get_message("deltele_success", location=location_name))

    async def cmd_set_item(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 3 or not parts[2].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!item set @username"))
            return
        target_username = parts[2][1:].lower()
        target_user = self.active_users.get(target_username)
        if not target_user:
            await self.highrise.chat(self.get_message("user_not_found", username=target_username))
            return
        try:
            outfit_response = await self.highrise.get_user_outfit(target_user.id)
            if not hasattr(outfit_response, "outfit") or not outfit_response.outfit:
                await self.highrise.chat(f"خطا: اطلاعات ظاهر برای @{target_username} در دسترس نیست.")
                return
            await self.highrise.set_outfit(outfit_response.outfit)
            await self.highrise.chat(self.get_message("set_item_success", username=target_username))
        except Exception as e:
            await self.highrise.chat(f"خطا در تغییر ظاهر ربات: {str(e)}")

    async def cmd_welcome(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = parts[:1] + ([" ".join(parts[1:])] if len(parts) > 1 else [])
        if len(parts) < 2:
            await self.highrise.chat(self.get_message("invalid_format", format="!welcome پیام"))
            return
        self.config["welcome_message"] = parts[1]
        self.save_config()
        await self.highrise.chat(f"پیام خوش‌آمدگویی به '{parts[1]}' تغییر کرد.")

    async def cmd_addadmin(self, user: User, parts: list):
        if not self.is_host(user.username):
            await self.highrise.chat("فقط Host می‌تواند از این دستور استفاده کند!")
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!addadmin @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username in self.config["admin_usernames"]:
            await self.highrise.chat(f"کاربر @{target_username} قبلاً ادمین است!")
            return
        self.config["admin_usernames"].append(target_username)
        self.save_config()
        await self.highrise.chat(f"کاربر @{target_username} با موفقیت به ادمین‌ها اضافه شد!")

    async def cmd_removeadmin(self, user: User, parts: list):
        if not self.is_host(user.username):
            await self.highrise.chat("فقط Host می‌تواند از این دستور استفاده کند!")
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!removeadmin @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username not in self.config["admin_usernames"]:
            await self.highrise.chat(f"کاربر @{target_username} در لیست ادمین‌ها نیست!")
            return
        if self.is_host(target_username):
            await self.highrise.chat(f"❌ @{target_username} رتبه Host دارد و نمی‌توان او را از ادمین‌ها حذف کرد!")
            return
        self.config["admin_usernames"].remove(target_username)
        self.save_config()
        await self.highrise.chat(f"کاربر @{target_username} با موفقیت از ادمین‌ها حذف شد!")

    async def cmd_addhost(self, user: User, parts: list):
        if user.username.lower() != "ad0ri":
            await self.highrise.chat("❌ دسترسی غیرمجاز!")
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!addhost @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username in self.config["host_usernames"]:
            await self.highrise.chat(f"کاربر @{target_username} از قبل Host است!")
            return
        self.config["host_usernames"].append(target_username)
        if target_username not in self.config["admin_usernames"]:
            self.config["admin_usernames"].append(target_username)
        self.save_config()
        await self.highrise.chat(f"👑 کاربر @{target_username} با موفقیت Host شد!")

    async def cmd_removehost(self, user: User, parts: list):
        if user.username.lower() != "ad0ri":
            await self.highrise.chat("❌ دسترسی غیرمجاز!")
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!removehost @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username not in self.config["host_usernames"]:
            await self.highrise.chat(f"کاربر @{target_username} در لیست Host‌ها نیست!")
            return
        if len(self.config["host_usernames"]) <= 1:
            await self.highrise.chat("❌ نمی‌توان آخرین Host را حذف کرد!")
            return
        self.config["host_usernames"].remove(target_username)
        self.save_config()
        await self.highrise.chat(f"کاربر @{target_username} از رتبه Host حذف شد.")

    async def cmd_listadd(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        if not self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("listadd_empty"))
            return
        admin_list = [f"@{username}" for username in self.config["admin_usernames"]]
        await self.highrise.chat(self.get_message("listadd_success", count=len(admin_list), admin_list="\n".join(admin_list)))

    async def cmd_freeze(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!freeze @username"))
            return
        target_username = parts[1][1:].lower()
        target_user = self.active_users.get(target_username)
        if not target_user:
            await self.highrise.chat(self.get_message("user_not_found", username=target_username))
            return
        if target_username in self.frozen_users:
            await self.highrise.chat(f"کاربر @{target_username} قبلاً فریز شده است.")
            return
        position = self.user_positions.get(target_username)
        if not position:
            await self.highrise.chat(f"موقعیت @{target_username} در دسترس نیست.")
            return
        async def freeze_loop():
            try:
                while target_username in self.frozen_users:
                    if target_username not in self.active_users:
                        self.frozen_users.pop(target_username, None)
                        break
                    await self.highrise.teleport(user_id=target_user.id, dest=position)
                    await sleep(1.0)
            except CancelledError:
                pass
            except Exception as e:
                logger.error(f"خطا در حلقه فریز برای {target_username}: {e}")
        task = create_task(freeze_loop())
        self.frozen_users[target_username] = task
        await self.highrise.chat(self.get_message("freeze_success", username=target_username))

    async def cmd_unfreeze(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!unfreeze @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username not in self.frozen_users:
            await self.highrise.chat(self.get_message("unfreeze_not_frozen", username=target_username))
            return
        task = self.frozen_users.pop(target_username)
        task.cancel()
        await self.highrise.chat(self.get_message("unfreeze_success", username=target_username))

    async def cmd_party(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 3 or (not parts[1].startswith("@") and parts[1] != "all") or not parts[2].isdigit():
            await self.highrise.chat(self.get_message("invalid_format", format="!party @username عدد یا !party all عدد"))
            return
        dance_number = parts[2]
        if dance_number not in self.emotes:
            await self.highrise.chat(f"رقص شماره {dance_number} وجود ندارد!")
            return
        emote = self.emotes[dance_number]
        duration = self.emote_durations.get(emote, 15.0)
        if parts[1] == "all":
            successful_dances = 0
            for username, target_user in self.active_users.items():
                if target_user.id == self.user_id:
                    continue
                await self.stop_dance(target_user)
                self.party_dances[username] = (emote, False)
                async def dance_loop(un=username, tu=target_user):
                    try:
                        while un in self.party_dances and self.party_dances[un][0] == emote:
                            if un not in self.active_users:
                                self.party_dances.pop(un, None)
                                break
                            await self.highrise.send_emote(emote, tu.id)
                            await sleep(duration)
                    except CancelledError:
                        pass
                task = create_task(dance_loop())
                self.dance_tasks[username] = task
                successful_dances += 1
                await sleep(0.5)
            await self.highrise.chat(self.get_message("party_all_success", dance_number=dance_number, count=successful_dances))
        else:
            target_username = parts[1][1:].lower()
            target_user = self.active_users.get(target_username)
            if not target_user:
                await self.highrise.chat(self.get_message("user_not_found", username=target_username))
                return
            await self.stop_dance(target_user)
            self.party_dances[target_username] = (emote, True)
            async def dance_loop():
                try:
                    while target_username in self.party_dances and self.party_dances[target_username][0] == emote:
                        if target_username not in self.active_users:
                            self.party_dances.pop(target_username, None)
                            break
                        await self.highrise.send_emote(emote, target_user.id)
                        await sleep(duration)
                except CancelledError:
                    pass
            task = create_task(dance_loop())
            self.dance_tasks[target_username] = task
            await self.highrise.chat(self.get_message("party_success", dance_number=dance_number, username=target_username))

    async def cmd_partys(self, user: User, parts: list):
        if user.username.lower() not in self.config["admin_usernames"]:
            await self.highrise.chat(self.get_message("no_permission"))
            return
        parts = [p.lower() for p in parts]
        if len(parts) != 2 or not parts[1].startswith("@"):
            await self.highrise.chat(self.get_message("invalid_format", format="!partys @username"))
            return
        target_username = parts[1][1:].lower()
        if target_username not in self.party_dances:
            await self.highrise.chat(self.get_message("partys_not_dancing", username=target_username))
            return
        await self.stop_dance(self.active_users[target_username])
        self.party_dances.pop(target_username, None)
        await self.highrise.chat(self.get_message("partys_success", username=target_username))

    async def cmd_loopchat(self, user: User, parts: list):
        admins_lower = [a.lower() for a in self.config.get("admin_usernames", [])]
        if user.username.lower() not in admins_lower:
            await self.highrise.chat("❌ این دستور مخصوص ادمین‌های ربات است!")
            return
        if len(parts) < 2:
            await self.highrise.chat("⚠️ فرمت اشتباه! فرمت صحیح: !loopchat پیام شما")
            return
        loop_message = " ".join(parts[1:])
        if hasattr(self, 'loopchat_task') and self.loopchat_task:
            self.loopchat_task.cancel()
        await self.highrise.chat(f"✅ حالت تکرار فعال شد! پیام: {loop_message}")
        async def loopchat_loop():
            try:
                while True:
                    await self.highrise.chat(loop_message)
                    await sleep(10.0)
            except CancelledError:
                pass
            except Exception as e:
                logger.error(f"خطا در loopchat: {e}")
        self.loopchat_task = create_task(loopchat_loop())

    async def cmd_emotebot(self, user: User, parts: list):
        admins_lower = [a.lower() for a in self.config.get("admin_usernames", [])]
        if user.username.lower() not in admins_lower:
            await self.highrise.chat("❌ این دستور مخصوص ادمین‌های ربات است!")
            return
        if len(parts) < 2:
            await self.highrise.chat("⚠️ فرمت اشتباه! نام یا شماره دنس را وارد کنید. مثال: !emotebot kpop")
            return
        input_emote = parts[1].strip().lower()
        actual_emote_name = self.emotes.get(input_emote)
        if not actual_emote_name and input_emote in self.emotes.values():
            actual_emote_name = input_emote
        if not actual_emote_name:
            await self.highrise.chat("❌ دنس یا شماره وارد شده در لیست دنس‌های ربات پیدا نشد!")
            return
        if self.user_id in self.dance_tasks:
            self.dance_tasks[self.user_id].cancel()
            self.dance_tasks.pop(self.user_id, None)
        await self.highrise.chat(f"✅ دنس ربات روی حالت تکرار همیشگی (Loop) تنظیم شد: [{input_emote}]")
        duration = self.emote_durations.get(actual_emote_name, 15.0)
        sleep_time = duration + 1.0
        async def new_emote_loop():
            try:
                while True:
                    await self.highrise.send_emote(actual_emote_name, self.user_id)
                    await sleep(sleep_time)
            except CancelledError:
                pass
            except Exception as e:
                logger.error(f"خطا در دنس مداوم ربات: {e}")
        self.dance_tasks[self.user_id] = create_task(new_emote_loop())


async def main():
    import os
    import asyncio
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    logger.info("تلاش برای بارگذاری متغیرهای محیطی...")
    room_id = os.getenv("ROOM_ID", "679b5758c5f97335c8316783")
    api_token = os.getenv("API_TOKEN", "9ac4315003044a2a18da757cbc0cc7e9eb0e60869c7750dcab2b7f0eaa926894")

    if not room_id or not api_token:
        logger.error("ROOM_ID یا API_TOKEN تنظیم نشده‌اند.")
        return

    class PingHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Bot is Alive!")
        def log_message(self, format, *args):
            return

    def run_web_server():
        try:
            port = int(os.getenv("PORT", 8080))
            server = HTTPServer(('0.0.0.0', port), PingHandler)
            logger.info(f"وب‌سرور زنده نگهدارنده روی پورت {port} فعال شد.")
            server.serve_forever()
        except Exception as e:
            logger.error(f"خطا در اجرای وب‌سرور پس‌زمینه: {e}")

    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    def handle_exception(loop, context):
        msg = context.get("exception", context["message"])
        logger.error(f"یک تسک پس‌زمینه با خطا مواجه شد اما مهار شد: {msg}")

    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(handle_exception)
    except Exception as le:
        logger.error(f"خطا در تنظیم exception handler: {le}")

    max_reconnect_attempts = 10
    attempt = 0
    while attempt < max_reconnect_attempts:
        try:
            room_id = os.environ.get("ROOM_ID", room_id)
            bot_instance = AdvancedBot()
            bot_def = BotDefinition(room_id=room_id, api_token=api_token, bot=bot_instance)
            logger.info(f"تلاش برای اتصال به سرور Highrise... روم: {room_id}")
            from highrise.__main__ import main as highrise_main
            await highrise_main([bot_def])
        except Exception as e:
            logger.error(f"اتصال WebSocket قطع شد یا خطا داد: {e}")
            try:
                await bot_instance.cleanup_tasks()
            except Exception:
                pass
            attempt += 1
            logger.info(f"انتظار برای اتصال مجدد... تلاش {attempt} از {max_reconnect_attempts}")
            await asyncio.sleep(6)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
