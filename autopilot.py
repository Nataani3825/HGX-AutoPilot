import ctypes
import hgx
import Hgx.Core
import time
import NLog
import threading

from ctypes import wintypes

######################################################################################################
########################################## CONFIGURATIONS ############################################
######################################################################################################

########################################## AUTO-RECOVERY #############################################

ar_auto_lock = True            #Automatic !lock target and !action attack is off by default
ar_auto_gs = False             #Turns the Optional recovery action on.  With this on the character will attempt this action first, then the heal action.  With it off, the character will only attempt to heal.
ar_auto_heal = True            #Turns the Primary recovery action on or off.  This is intended to be used for the heal button.
ar_auto_abort = True           #Automatic !abort prior to recovery actions is on by default

ar_val_lowhp = 500             #ar_val_lowhp is the HP value that will cause damage events to trigger.  When Current HP <= ar_val_lowhp, the sequence of actions fires

ar_button_heal = 0x70          #Virtual Key Codes must be used to define your heal and gv buttons.  Default Virtual Key Code for Heal is F1
ar_button_gs = 0x78            #Virtual Key Codes must be used to define your heal and gv buttons.  Default Virtual Key Code for GS is F9

ar_delay_lock = 0.1            #This is the amount of time the script will wait after calling the !lock and !action commands, before taking the next actions.  0.1s is recommended.
ar_delay_abort = 0.1           #This is the amount of time the script will wait after calling the !abort command, before taking the next actions.  0.1s is recommended.
ar_delay_action = 2.5          #This is the amount of time the script will wait between the GV Button press and the Heal button press.  There are a couple of other small delays in place that add up to about 0.5s.

# Mapping function keys to their virtual key codes
# For codes, check https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
function_key_to_vk = {
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B
}

########################################### AUTO-COMMAND #############################################

ac_auto_command = True         #Turns auto command on or off
ac_auto_loop = True            #If true, the character will keep attempting the commanded action until told to do something else.
ac_auto_abort = True           #If true, the character will abort before acting on a new command to ensure quick responsiveness.
ac_val_role = 'Priority'               #Default role.  Note that you cannot set Master as default, this must be spoken in chat for all bots to hear.
ac_global_assist = True        #If true, assist roles will assist anyone who asks, not just the master role.  Looping is disabled for assist actions.

ac_val_follow = ['AC Follow', 'follow', 'Follow', 'fall', 'Fall']                                                     #Follow commands for all bots, add more here.
ac_val_guard = ['AC Guard', 'guard', 'Guard', 'shield', 'Shield']                                                     #Guard commands for Priority role bots, add more here.
ac_val_attack = ['AC Attack', 'their time', 'Their time', 'at their', 'At their','attack', 'Attack']                  #Attack commands for Alternate role bots, add more here.
ac_val_heal = ['AC Heal', 'kd', 'KD', 'healer, to', 'Healer, to', 'my wounds', 'My wounds']                           #Assist commands for Assist role bots, add more here.
ac_val_stop = ['AC Stop', 'stop', 'stand your ground', 'Stand your ground', 'hold here', 'Hold Here']                 #Stop commands for all bots, add more here.

ac_announce = True
ac_val_kd = ['trip you', 'trips you', 'knocked down', 'knocks you down', 'to your knees']

ac_delay_action = 3.0           #The amount of time to wait between action attempts when Loop is on.

########################################### AUTO-ACTION ##############################################

aa_auto_cs = False              #Turns Auto-CS on or off.  Only one swift action may be turned on at a time.
aa_auto_disarm = False          #Turns Auto-Disarm on or off.  Only one swift action may be turned on at a time.
aa_auto_knockdown = False       #Turns Auto-Knockdown on or off.  Only one swift action may be turned on at a time.
aa_auto_taunt = False           #Turns Auto-Taunt on or off.  Only one swift action may be turned on at a time.

########################################## AUTO-BANKING ##############################################

ab_auto_bank = True             #Turns automatic banking on or off by default.

ab_area_withdrawals = {
    "Zerial": 15000,
    "Forge": 300000000,
    # Add more areas and their corresponding withdraw amounts here
}

########################################### DEBUGGING ################################################

ap_debugging = False            #ap_debugging is turned off by default.  Turning it on will cause the system to send the player tells at various check points.  This may cause performance issues.

########################################## AUTO-DAMAGE ###############################################

# LegendaryArcherBow(nLevel, bEgo)
# DivineSlingerBullet(nCharacterLevel, nClericLevels)
# StaffMaster(nCharacterLevel, nWeaponMasterLevels)
# LegendaryRangerBow(nLevel, bEgo)

ad_auto_damage = True
ad_slinger = True
ad_config = {
    "Belle Morte D'Gypsie" : hgx.LegendaryArcherBow(52, False),
	" Kleb's 2.0 AA": hgx.LegendaryArcherBow(61, False),  
    "Kleb's 2.0 AA": hgx.LegendaryArcherBow(61, False), 
	" Kleb's 2.1 AA": hgx.LegendaryArcherBow(61, False),
	"Kleb's 2.1 AA": hgx.LegendaryArcherBow(61, False),
	" Kleb's 2.0 Slinger"  : hgx.DivineSlingerBullet(61, 38),
	"Kleb's 2.0 Slinger"  : hgx.DivineSlingerBullet(61, 38),
    " Kleb's 2.0 Ranger"  : hgx.LegendaryRangerBow(61, False),
    "Kleb's 2.0 Ranger"  : hgx.LegendaryRangerBow(61, False),
    "Milli A Vanilli" : hgx.LegendaryArcherBow(75, True),
    "Bogli Sagittarius" : hgx.LegendaryArcherBow(73, True)
	}
ad_breach = ['Rakshasa', 'Raja','Superior Raja']

######################################################################################################
########################################## SYSTEM GLOBALS ############################################
########################################## DO NOT MODIFY #############################################
######################################################################################################

gb_character = None
gb_player = None
gb_target = None

ar_auto_recovery = False
ar_drinking = False

ac_break_follow = False
ac_break_attack = False
ac_break_guard = False
ac_break_assist = False
ac_follow_thread = None
ac_attack_thread = None
ac_guard_thread = None
ac_assist_thread = None
ac_val_master = None

ad_damagetypes = None
ad_adjustment = None
ad_commands = {
	Hgx.Core.DamageType.Acid : "!damac",
	Hgx.Core.DamageType.Cold : "!damco",
	Hgx.Core.DamageType.Electrical : "!damel",
	Hgx.Core.DamageType.Fire : "!damfi",
	Hgx.Core.DamageType.Sonic : "!damso",
	Hgx.Core.DamageType.Divine : "!damdi",
	Hgx.Core.DamageType.Magical : "!damma",
	Hgx.Core.DamageType.Negative : "!damne",
	Hgx.Core.DamageType.Positive : "!dampo"}

kernel32 = ctypes.windll.kernel32
pointer_offset = 0x0053165C 
pointer_offset2 = 0x2B8
pointer_offset3 = 0x4C
main_exe_offset = 0x00400000
process_handle = None
pointer1_address = main_exe_offset + pointer_offset
hp_address = None
user32 = ctypes.WinDLL('user32', use_last_error=True)
foreground_window = None
pid = None
ASFW_ANY = -1
thread_lock = threading.Lock()

logger = NLog.LogManager.GetLogger(__file__)


######################################################################################################
############################################ FUNCTIONS ###############################################
######################################################################################################

def help():
    global gb_character
    hgx.Messages.Chat('/tell "{0}" Auto Recovery commands:\
        \n"AR Toggle" - Toggles Auto Recovery on or off\
        \n"AR HP [integer]" - Sets the trigger HP to drink a potion\
        \n"AR Lock" - Turns auto locking on or off\
        \n"AR Abort" - Turns auto abort on or off\
        \n"AR Heal" - Turns auto healing on or off\
        \n"AR GS" - Turns auto gs on or off\
        \n"AR Button Heal [F1 - F12]" - Sets the keyboard binding for the heal button\
        \n"AR Button GS [F1 - F12]" - Sets the keyboard binding for the gs button\
        \n\
        \nAuto Command commands:\
        \n"AC Toggle" - Toggles Auto Commands on or off\
        \n"AC Loop" - When off the character will action one time.  When on the character will action until given a stop command.\
        \n"AC Master" - Sets the role of the character to "master".  All other instances running this script will set the character as master.\
        \n"AC Priority" - Sets the role of the character to "priority".  All other instances running this script will set the character as Priority.\
        \n"AC Alternate" - Sets the role of the character to "alternate".  All other instances running this script will set the character as Alternate.\
        \n"AC Assist" - Sets the role of the character to "assist".  All other instances running this script will set the character as assist.\
        \n"AC Global Assist" - Turns Global Assist on or off.  When on, an assist role character will not loop assists, and will assist any player who issues a heal command.\
        \n"AC Portal [integer]" - All bots listening will portal to the designated server.\
        \n"AC Pcscry" - All bots listening will initiate the pcscry converation.\
        \n"AC Delay [decimal]" - The number of seconds the script will wait between actions attempts when looping is on.\
        \n\
        \nAuto Action commands:\
		\n"AA CS" - Toggles Auto Called Shot on or off\
		\n"AA DS" - Toggles Auto Disarm on or off\
		\n"AA KD" - Toggles Auto Knockdown on or off\
		\n"AA TT" - Toggles Auto Taunt on or off\
        \n\
        \nAuto Banking commands:\
        \n"AB Help" - Displays this help message in your chat.\
        \n"AB Toggle" - Toggles Auto Banking on or off\
        \n\
        \nAuto Damage commands:\
        \n"AD Toggle" - Toggles Auto Damage on or off\
        '.format(gb_player))

def autoRecovery_actionDelay():
    global ar_drinking
    global gb_character
    global ar_auto_lock
    global ar_delay_action
    global ar_delay_lock

    time.sleep(ar_delay_action)
    ar_drinking = False

    if ar_auto_lock == True:
        hgx.Messages.Chat("!action attack locked")
        time.sleep(ar_delay_lock)

def autoCommand_followTarget():
    global ac_break_follow
    global ar_drinking
    ac_target = gb_player
    i = 0
    while ac_break_follow == False: 
        if ac_break_follow == True:
            break
        if ar_drinking == False:
            if i == 10:
                hgx.Messages.Chat("!abort")   
                i = 0        
            if ac_break_follow == False:
                hgx.Messages.Chat("!action aso target")
                hgx.Messages.Chat('/tell "{0}" !target'.format(ac_target)) 
                i = i + 1
            time.sleep(ac_delay_action)

def autoCommand_followThreadCreation():
    global ac_follow_thread
    global ac_break_follow
    global ac_break_guard
    global ac_break_attack
    global ac_break_assist
    with thread_lock:
        if ac_attack_thread is not None and ac_attack_thread.is_alive():
            ac_break_attack = True
        if ac_guard_thread is not None and ac_guard_thread.is_alive():
            ac_break_guard = True
        if ac_assist_thread is not None and ac_assist_thread.is_alive():
            ac_break_assist = True
        ac_break_follow = False
        ac_follow_thread = threading.Thread(target=autoCommand_followTarget)
        ac_follow_thread.setDaemon(True)
        ac_follow_thread.start()

def autoCommand_guardTarget():
    global ac_break_guard
    global ar_drinking

    while ac_break_guard == False:
        if ac_break_guard == True:
            break
        elif ar_drinking == False:
            if aa_auto_cs == True:
                hgx.Messages.Chat("!action attack+cs master:opponent")

            elif aa_auto_disarm == True:
                hgx.Messages.Chat("!action attack+dis master:opponent")

            elif aa_auto_knockdown == True:
                hgx.Messages.Chat("!action attack+kd master:opponent")

            elif aa_auto_taunt == True:
                hgx.Messages.Chat("!action attack+taunt master:opponent")
            
            else:
                hgx.Messages.Chat("!action attack master:opponent")

            time.sleep(ac_delay_action)

def autoCommand_guardThreadCreation():
    global ac_guard_thread
    global ac_break_follow
    global ac_break_guard
    global ac_break_attack
    global ac_break_assist
    with thread_lock:
        if ac_attack_thread is not None and ac_attack_thread.is_alive():
            ac_break_attack = True
        if ac_follow_thread is not None and ac_follow_thread.is_alive():
            ac_break_follow = True
        if ac_assist_thread is not None and ac_assist_thread.is_alive():
            ac_break_assist = True
        ac_break_guard = False
        hgx.Messages.Chat('/tell "{0}" !abort'.format(gb_character))
        ac_guard_thread = threading.Thread(target=autoCommand_guardTarget)
        ac_guard_thread.setDaemon(True)
        ac_guard_thread.start()

def autoCommand_attackTarget():
    global ac_break_attack
    global ar_drinking
    while ac_break_attack == False:
        if ac_break_attack == True:
            break
        elif ar_drinking == False:
            if ap_debugging == True:
                hgx.Messages.Chat('/tell "{0}" Attempted Attack Loop'.format(gb_character)) #ap_debugging

            if aa_auto_cs == True:
                hgx.Messages.Chat("!action attack+cs master:locked")

            elif aa_auto_disarm == True:
                hgx.Messages.Chat("!action attack+dis master:locked")

            elif aa_auto_knockdown == True:
                hgx.Messages.Chat("!action attack+kd master:locked")

            elif aa_auto_taunt == True:
                hgx.Messages.Chat("!action attack+taunt master:locked")

            else:
                hgx.Messages.Chat("!action attack master:locked")

            time.sleep(ac_delay_action)

def autoCommand_attackThreadCreation():
    global ac_attack_thread
    global ac_break_follow
    global ac_break_guard
    global ac_break_attack
    global ac_break_assist
    with thread_lock:
        if ac_guard_thread is not None and ac_guard_thread.is_alive():
            ac_break_guard = True
        if ac_follow_thread is not None and ac_follow_thread.is_alive():
            ac_break_follow = True
        if ac_assist_thread is not None and ac_assist_thread.is_alive():
            ac_break_assist = True
        ac_break_attack = False
        ac_attack_thread = threading.Thread(target=autoCommand_attackTarget)
        ac_attack_thread.setDaemon(True)
        ac_attack_thread.start()

def autoCommand_assistTarget():
    global ac_break_assist
    global ar_drinking
    ac_target = gb_player
    i = 0
    while ac_break_assist == False:
        if ac_break_assist == True:
            break
        if ar_drinking == False:
            if i == 10:
                hgx.Messages.Chat("!abort")   
                i = 0    
            else:
                hgx.Messages.Chat("!action aso target")
                hgx.Messages.Chat('/tell "{0}" !target'.format(ac_target))
                i = i + 1
            time.sleep(ac_delay_action)

def autoCommand_assistThreadCreation():
    global ac_assist_thread
    global ac_break_follow
    global ac_break_guard
    global ac_break_attack
    global ac_break_assist
    with thread_lock:
        if ac_guard_thread is not None and ac_guard_thread.is_alive():
            ac_break_guard = True
        if ac_follow_thread is not None and ac_follow_thread.is_alive():
            ac_break_follow = True
        if ac_attack_thread is not None and ac_attack_thread.is_alive():
            ac_break_attack = True
        ac_break_assist = False
        ac_assist_thread = threading.Thread(target=autoCommand_assistTarget)
        ac_assist_thread.setDaemon(True)
        ac_assist_thread.start()

def autoDamage_update():
    if ad_damagetypes and gb_target:

        c = hgx.Characters[gb_target]
		
        if ad_adjustment:
            c = ad_adjustment.Adjust(c)
		
        if not "Chosen of Tiamat" in gb_target:
            (dam, dt) = max((w.ExpectedDamageAgainst(c), w.damage_type) for w in ad_damagetypes)
        else:
            dt = hgx.Core.DamageType.Divine

        try:
            hgx.Messages.Chat(ad_commands[dt])
            if ad_slinger:
                if gb_target in ad_breach:
                    hgx.Messages.Chat("!dambr")
                else:
                    hgx.Messages.Chat("!damhe")


        except KeyError:
            hgx.Messages.Chat('/tell "{0}" KeyError'.format(gb_character))

def autoDamage_updatePlayer():
    global ad_damagetypes
    global gb_character
    global gb_character_stripped

    gb_character = hgx.Encounters.PlayerCharacter
    gb_character_stripped = gb_character.strip()
    ad_damagetypes = list(ad_config[gb_character])

######################################################################################################
############################################## MAIN ##################################################
######################################################################################################
        
def on_logread(sender, e):
    global gb_character, gb_player, gb_target, ap_debugging
    global process_handle, hp_address, pid, foreground_window
    global ar_auto_recovery, ar_drinking, ar_val_lowhp, ar_auto_lock, ar_button_heal, ar_auto_heal, ar_button_gs, ar_auto_gs, ar_auto_abort, ar_delay_lock, ar_delay_abort, ar_delay_action
    global ac_auto_command, ac_auto_loop, ac_delay_action, ac_break_follow, ac_break_attack, ac_break_guard, ac_break_assist, ac_val_role, ac_val_master, ac_global_assist, ac_auto_abort, ac_announce
    global aa_auto_cs, aa_auto_disarm, aa_auto_knockdown, aa_auto_taunt
    global ab_auto_bank
    global ad_auto_damage, ad_slinger, ad_damagetypes, ad_adjustment
    
    gb_player = e.Line[:(e.Line.find(":"))]
    gb_player_stripped = gb_player.strip()
    
    gb_character = hgx.Encounters.PlayerCharacter
    gb_character_stripped = gb_character.strip()

    if " damages " in e.Line and ar_auto_recovery == True and ar_drinking == False:
        damage_event = hgx.Hgx.Core.DamageGameEvent()
        damage_event.RawData = e.Line
        parsed_event = hgx.Hgx.Services.Parsers.DamageGameEventParser.Parse(damage_event)
        if parsed_event.Defender == gb_character:
            buffer2 = ctypes.c_uint16()
            ctypes.windll.kernel32.ReadProcessMemory(process_handle, hp_address, ctypes.byref(buffer2), ctypes.sizeof(buffer2), None)
            current_HP = buffer2.value
            if ap_debugging == True:    
                hgx.Messages.Chat('/tell "{0}" Precheck current_HP is {1}. ar_val_lowhp is {2}'.format(gb_character,current_HP,ar_val_lowhp)) #ap_debugging
            if current_HP <= ar_val_lowhp:
                ar_try_recover = False
                i = 0
                user32.AllowSetForegroundWindow(ASFW_ANY)
                user32.SetForegroundWindow(foreground_window)
                
                while ar_try_recover == False and i < 10:
                    if ctypes.windll.user32.GetForegroundWindow() == foreground_window:
                        if ar_auto_lock == True:
                            hgx.Messages.Chat("!lock opponent")
                            if ap_debugging == True:
                                hgx.Messages.Chat('/tell "{0}" Attempted Lock'.format(gb_character)) #ap_debugging
                            time.sleep(ar_delay_lock) 
                        if ar_auto_abort == True:
                            hgx.Messages.Chat('!abort')
                            if ap_debugging == True:
                                hgx.Messages.Chat('/tell "{0}" Attempted Abort'.format(gb_character)) #ap_debugging
                            time.sleep(ar_delay_abort)  
                        if ar_auto_heal == True:
                            ctypes.windll.user32.keybd_event(ar_button_heal, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(ar_button_heal, 0, 0x0002, 0)
                            if ap_debugging == True:
                                hgx.Messages.Chat('/tell "{0}" Pressed Heal Button from Main'.format(gb_character)) #ap_debugging
                        if ar_auto_gs == True:
                            ctypes.windll.user32.keybd_event(ar_button_gs, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(ar_button_gs, 0, 0x0002, 0)
                            if ap_debugging == True:
                                hgx.Messages.Chat('/tell "{0}" Pressed GV Button from Main'.format(gb_character)) #ap_debugging

                        ar_try_recover = True
                        ar_drinking = True
                        ar_actionDelay_thread = threading.Thread(target=autoRecovery_actionDelay)
                        ar_actionDelay_thread.setDaemon(True)
                        ar_actionDelay_thread.start()
               
                    time.sleep(0.05)
                    i += 1   
    
    if " attacks " in e.Line:
        if ad_auto_damage == True:
            attack_event = hgx.Hgx.Core.AttackGameEvent()
            attack_event.RawData = e.Line
            parsed_event = hgx.Hgx.Services.Parsers.AttackGameEventParser.Parse(attack_event)

            if parsed_event.Attacker == gb_character_stripped and parsed_event.Defender != gb_target:
                gb_target = parsed_event.Defender
                autoDamage_update()

        if aa_auto_cs == True and ac_auto_command == False:
            hgx.Messages.Chat("!action cs opponent")

        elif aa_auto_disarm == True and ac_auto_command == False:
            hgx.Messages.Chat("!action dis opponent")

        elif aa_auto_knockdown == True and ac_auto_command == False:
            hgx.Messages.Chat("!action kd opponent")

        elif aa_auto_taunt == True and ac_auto_command == False:
            hgx.Messages.Chat("!action taunt opponent")

    elif any(substring in str(e.Line) for substring in ac_val_follow) and ac_auto_command and ac_val_role != 'Master' and gb_player_stripped == ac_val_master:
        if gb_player_stripped != gb_character_stripped:
            if ac_auto_abort == True:
                hgx.Messages.Chat("!abort")
            if ac_auto_loop == False:
                hgx.Messages.Chat("!action aso target")
                hgx.Messages.Chat('/tell "{0}" !target'.format(gb_player))    
            else:
                if ap_debugging == True:
                    hgx.Messages.Chat('/tell "{0}" Entered Follow Thread Else Condition'.format(gb_character)) #ap_debugging  
                autoCommand_followThreadCreation()

    elif any(substring in str(e.Line) for substring in ac_val_guard) and ac_auto_command and ac_val_role == 'Priority' and gb_player_stripped == ac_val_master:
        if gb_player_stripped != gb_character_stripped:
            if ac_auto_abort == True:
                hgx.Messages.Chat("!abort")
            if ac_auto_loop == False:
                hgx.Messages.Chat("!action attack master:opponent") 
            else:
                if ap_debugging == True:
                    hgx.Messages.Chat('/tell "{0}" Entered Guard Thread Else Condition'.format(gb_character)) #ap_debugging  
                autoCommand_guardThreadCreation()

    elif any(substring in str(e.Line) for substring in ac_val_attack) and ac_auto_command and gb_player_stripped == ac_val_master:
        if gb_player_stripped == gb_character_stripped and ac_val_role == 'Master':
            hgx.Messages.Chat("!lock target")

        elif gb_player != gb_character and ac_val_role == 'Alternate':
            if ac_auto_loop == False:
                time.sleep(ac_delay_action)
                if ac_auto_abort == True:
                    hgx.Messages.Chat("!abort")
                hgx.Messages.Chat("!action attack master:locked") 
            else:
                if ap_debugging == True:
                    hgx.Messages.Chat('/tell "{0}" Entered Attack Thread Else Condition'.format(gb_character)) #ap_debugging  
                if ac_auto_abort == True:
                    hgx.Messages.Chat("!abort")
                autoCommand_attackThreadCreation()

    elif any(substring in str(e.Line) for substring in ac_val_heal) and ac_auto_command and ac_val_role == 'Assist':
        if gb_player_stripped != gb_character_stripped:
            if ac_auto_abort == True:
                hgx.Messages.Chat("!abort")
            if ac_global_assist == True:
                hgx.Messages.Chat("!action aso target")
                hgx.Messages.Chat('/tell "{0}" !target'.format(gb_player))
            elif ac_auto_loop == False and gb_player_stripped == ac_val_master:
                hgx.Messages.Chat("!action aso target")
                hgx.Messages.Chat('/tell "{0}" !target'.format(gb_player))
            elif ac_auto_loop == True and gb_player_stripped == ac_val_master:
                if ap_debugging == True:
                    hgx.Messages.Chat('/tell "{0}" Entered Assist Thread Else Condition'.format(gb_character)) #ap_debugging  
                autoCommand_assistThreadCreation()
              
    elif any(substring in str(e.Line) for substring in ac_val_stop) and ac_auto_command and ac_val_role != 'Master':  
        if ac_auto_command == True:
            ac_break_follow = True
            ac_break_attack = True
            ac_break_guard = True
            ac_break_assist = True
            hgx.Messages.Chat("!abort")
    
    elif any(substring in str(e.Line) for substring in ac_val_kd) and ac_announce:  
        hgx.Messages.Chat("/tk KD")

    elif "AC RSM" in e.Line and ac_auto_command and gb_player_stripped == ac_val_master:
        hgx.Messages.Chat("!action rsm self")

    elif "AC Master" in e.Line:
        if gb_player_stripped == gb_character_stripped:
            ac_val_role = 'Master' 
            ac_val_master = gb_character_stripped
            hgx.Messages.Chat('/tell "{0}" !role Master'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" Auto Command Role set to "Master"'.format(gb_player))
        else:
            ac_val_master = gb_player_stripped
            hgx.Messages.Chat('/tell "{0}" !role Master'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" {1} set {0} to "Master"'.format(gb_player,gb_character))

    elif "AC Priority" in e.Line:
        if gb_player_stripped == gb_character_stripped:
            ac_val_role = 'Priority' 
            hgx.Messages.Chat('/tell "{0}" !role Priority'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" Auto Command Role set to "Priority"'.format(gb_player))
        else:
            hgx.Messages.Chat('/tell "{0}" !role Priority'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" {1} set {0} to "Priority"'.format(gb_player,gb_character))

    elif "AC Alternate" in e.Line:
        if gb_player_stripped == gb_character_stripped:
            ac_val_role = 'Alternate' 
            hgx.Messages.Chat('/tell "{0}" !role Alternate'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" Auto Command Role set to "Alternate"'.format(gb_player))
        else:
            hgx.Messages.Chat('/tell "{0}" !role Alternate'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" {1} set {0} to "Alternate"'.format(gb_player,gb_character))

    elif "AC Assist" in e.Line:
        if gb_player_stripped == gb_character_stripped:
            ac_val_role = 'Assist' 
            hgx.Messages.Chat('/tell "{0}" !role Assist'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" Auto Command Role set to "Assist"'.format(gb_player))
        else:
            hgx.Messages.Chat('/tell "{0}" !role Assist'.format(gb_player))
            hgx.Messages.Chat('/tell "{0}" {1} set {0} to "Assist"'.format(gb_player,gb_character))
        
    elif "AC Portal" in e.Line and ac_auto_command:
        start_index = e.Line.find("AC Portal ") + len("AC Portal ")
        chat_value = e.Line[start_index:].strip() 
        server = int(chat_value) 
        hgx.Messages.Chat('!portal {0}'.format(server))

    elif "AC Pcscry" in e.Line and ac_auto_command:
        hgx.Messages.Chat('!pcscry')

    elif "You are now in " in e.Line:
        if ad_auto_damage:
            if 'Oinos' in e.Line:
                ad_adjustment = Hgx.Core.HadesAdjustment()
            else:
                ad_adjustment = None

        if ac_auto_command:
            hgx.Messages.Chat("!abort")

        if ab_auto_bank:
            for ab_area, ab_amount in ab_area_withdrawals.items():
                if ab_area in e.Line:
                    hgx.Messages.Chat("!wallet deposit all")
                    time.sleep(0.1)
                    hgx.Messages.Chat('!wallet withdraw {0}'.format(ab_amount))

    elif gb_player_stripped == gb_character_stripped:

        if "AP " in e.Line:

            if e.Line.find("AP Help") != -1:
                help()

            elif e.Line.find("AP Filter") != -1:
                hgx.Messages.Chat("!filter brief")
                hgx.Messages.Chat("!filter sr")
                hgx.Messages.Chat("!filter save")
                hgx.Messages.Chat("!filter check")
                hgx.Messages.Chat("!filter dispel")
                hgx.Messages.Chat("!filter restore")

            elif e.Line.find("AP Debugging") != -1:
                if ap_debugging == True:
                    ap_debugging = False
                    hgx.Messages.Chat('/tell "{0}" Auto Pilot Debugging OFF'.format(gb_player))
                else:
                    ap_debugging = True
                    hgx.Messages.Chat('/tell "{0}" Auto Pilot Debugging ON\nTHIS MAY CAUSE PERFORMANCE ISSUES'.format(gb_player))  

        elif "AR " in e.Line:

            if e.Line.find("AR Toggle") != -1:
                if ar_auto_recovery == False:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Recovery ON.'.format(gb_player))
                    ar_auto_recovery = True
                    foreground_window = ctypes.windll.user32.GetForegroundWindow()
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(foreground_window, ctypes.byref(pid))
                    process_handle = kernel32.OpenProcess(0x0400 | 0x0010, False, pid.value) # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
                    if hp_address == None:
                        buffer = ctypes.c_uint32()
                        ctypes.windll.kernel32.ReadProcessMemory(process_handle, pointer1_address, ctypes.byref(buffer), ctypes.sizeof(buffer), None)
                        pointer2_address = buffer.value
                        pointer2_address = pointer2_address + pointer_offset2
                        buffer = ctypes.c_uint32()
                        ctypes.windll.kernel32.ReadProcessMemory(process_handle, pointer2_address, ctypes.byref(buffer), ctypes.sizeof(buffer), None)
                        hp_address = buffer.value
                        hp_address = hp_address + pointer_offset3
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Recovery OFF.'.format(gb_player))
                    ar_auto_recovery = False
                    hp_address = None
            
            elif e.Line.find("AR Lock") != -1:
                if ar_auto_lock == True:
                    ar_auto_lock = False
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Locking OFF'.format(gb_player))
                else:
                    ar_auto_lock = True
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Locking ON'.format(gb_player))

            elif e.Line.find("AR Abort") != -1:
                if ar_auto_abort == True:
                    ar_auto_abort = False
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Abort OFF'.format(gb_player))
                else:
                    ar_auto_abort = True
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Abort ON'.format(gb_player))

            elif e.Line.find("AR Heal") != -1:
                if ar_auto_heal == True:
                    ar_auto_heal = False
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Healing OFF'.format(gb_player))
                else:
                    ar_auto_heal = True
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto Healing ON'.format(gb_player))

            elif e.Line.find("AR GS") != -1:
                if ar_auto_gs == True:
                    ar_auto_gs = False
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto GS OFF'.format(gb_player))
                else:
                    ar_auto_gs = True
                    hgx.Messages.Chat('/tell "{0}" Auto Recovery Auto GS ON'.format(gb_player))

            elif "AR HP " in e.Line:
                start_index = e.Line.find("AR HP ") + len("AR HP ")
                chat_value = e.Line[start_index:].strip() 
                ar_val_lowhp = int(chat_value) 
                hgx.Messages.Chat('/tell "{0}" Auto Recovery Low HP Threshold set to {1}'.format(gb_player,ar_val_lowhp))

            elif "AR Delay Lock " in e.Line:
                start_index = e.Line.find("AR Delay Lock ") + len("AR Delay Lock ")
                chat_value = e.Line[start_index:].strip() 
                ar_delay_lock = int(chat_value) 
                hgx.Messages.Chat('/tell "{0}" Auto Recovery Delay Lock set to {1}'.format(gb_player,ar_delay_lock))

            elif "AR Delay Abort " in e.Line:
                start_index = e.Line.find("AR Delay Abort ") + len("AR Delay Abort ")
                chat_value = e.Line[start_index:].strip() 
                ar_delay_abort = int(chat_value) 
                hgx.Messages.Chat('/tell "{0}" Auto Recovery Delay Abort set to {1}'.format(gb_player,ar_delay_abort))

            elif "AR Delay Action " in e.Line:
                start_index = e.Line.find("AR Delay Action ") + len("AR Delay Action ")
                chat_value = e.Line[start_index:].strip() 
                ar_delay_action = int(chat_value) 
                hgx.Messages.Chat('/tell "{0}" Auto Recovery Delay Action set to {1}'.format(gb_player,ar_delay_action))

            elif "AR Button Heal " in e.Line:
                start_index = e.Line.find("AR Button Heal ") + len("AR Button Heal ")
                button_input = e.Line[start_index:].strip()
                if button_input in function_key_to_vk:
                    ar_button_heal = function_key_to_vk[button_input]
                    hgx.Messages.Chat('/tell "{0}" Heal Potion button set to {1}.'.format(gb_player, button_input))
                else:
                    hgx.Messages.Chat('/tell "{0}" Invalid input: {1}. Please enter a valid key (F1 - F12).'.format(gb_player, button_input))

            elif "AR Button GS " in e.Line:
                start_index = e.Line.find("AR Button GS ") + len("AR Button GS ")
                button_input = e.Line[start_index:].strip()
                if button_input in function_key_to_vk:
                    ar_button_gs = function_key_to_vk[button_input]
                    hgx.Messages.Chat('/tell "{0}" GS button set to {1}.'.format(gb_player, button_input))
                else:
                    hgx.Messages.Chat('/tell "{0}" Invalid input: {1}. Please enter a valid key (F1 - F12).'.format(gb_player, button_input))

        elif "AC " in e.Line:

            if e.Line.find("AC Toggle") != -1:
                if ac_auto_command == False:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Command ON.'.format(gb_player))
                    ac_auto_command = True
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Command OFF.'.format(gb_player))
                    ac_auto_command = False

            elif e.Line.find("AC Loop") != -1:
                if ac_auto_loop == True:
                    ac_auto_loop = False
                    hgx.Messages.Chat('/tell "{0}" Auto Command Looping OFF'.format(gb_player))
                else:
                    ac_auto_loop = True
                    hgx.Messages.Chat('/tell "{0}" Auto Command Looping ON'.format(gb_player))

            elif e.Line.find("AC Global Assist") != -1:
                if ac_global_assist == True:
                    ac_global_assist = False
                    hgx.Messages.Chat('/tell "{0}" Auto Command Global Assist OFF'.format(gb_player))
                else:
                    ac_global_assist = True
                    hgx.Messages.Chat('/tell "{0}" Auto Command Global Assist ON'.format(gb_player))

            elif e.Line.find("AC Announce") != -1:
                if ac_announce == True:
                    ac_announce = False
                    hgx.Messages.Chat('/tell "{0}" Auto Command Announce OFF'.format(gb_player))
                else:
                    ac_announce = True
                    hgx.Messages.Chat('/tell "{0}" Auto Command Announce ON'.format(gb_player))

            elif e.Line.find("AC Abort") != -1:
                if ac_auto_abort == True:
                    ac_auto_abort = False
                    hgx.Messages.Chat('/tell "{0}" Auto Command Auto Abort OFF'.format(gb_player))
                else:
                    ac_auto_abort = True
                    hgx.Messages.Chat('/tell "{0}" Auto Command Auto Abort ON'.format(gb_player))
            
            elif "AC Delay " in e.Line:
                start_index = e.Line.find("AC Delay ") + len("AC Delay ")
                chat_value = e.Line[start_index:].strip() 
                ac_delay_action = float(chat_value) 
                hgx.Messages.Chat('/tell "{0}" Auto Command Action Delay set to {1}'.format(gb_player,ac_delay_action))

        elif "AA " in e.Line:

            if e.Line.find("AA CS") != -1:
                if aa_auto_cs == True:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Called Shot swift action OFF.'.format(gb_player))
                    aa_auto_cs = False
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Called Shot swift action ON.  All other switft actions turned OFF'.format(gb_player))
                    aa_auto_cs = True
                    aa_auto_disarm = False
                    aa_auto_knockdown = False
                    aa_auto_taunt = False

            elif e.Line.find("AA DS") != -1:
                if aa_auto_disarm == True:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Disarm swift action OFF.'.format(gb_player))
                    aa_auto_disarm = False
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Disarm swift action ON.  All other switft actions turned OFF'.format(gb_player))
                    aa_auto_disarm = True
                    aa_auto_cs = False
                    aa_auto_knockdown = False
                    aa_auto_taunt = False

            elif e.Line.find("AA KD") != -1:
                if aa_auto_knockdown == True:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Knockdown swift action OFF.'.format(gb_player))
                    aa_auto_knockdown = False
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Knockdown swift action ON.  All other switft actions turned OFF'.format(gb_player))
                    aa_auto_knockdown = True
                    aa_auto_cs = False
                    aa_auto_disarm = False
                    aa_auto_taunt = False

            elif e.Line.find("AA TT") != -1:
                if aa_auto_taunt == True:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Taunt swift action OFF.'.format(gb_player))
                    aa_auto_taunt = False
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto-Taunt swift action ON.  All other switft actions turned OFF'.format(gb_player))
                    aa_auto_taunt = True
                    aa_auto_cs = False
                    aa_auto_disarm = False
                    aa_auto_knockdown = False

        elif "AD " in e.Line:

            if e.Line.find("AD Toggle") != -1:
                if ad_auto_damage == False:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Damage ON.'.format(gb_player))
                    ad_auto_damage = True
                    autoDamage_updatePlayer()
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Damage OFF.'.format(gb_player))
                    ad_auto_damage = False

            if e.Line.find("AD Slinger") != -1:
                if ad_slinger == False:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Damage Slinger ON.'.format(gb_player))
                    ad_slinger = True
                    autoDamage_updatePlayer()
                else:
                    hgx.Messages.Chat('/tell "{0}" Toggled Auto Damage OFF.'.format(gb_player))
                    ad_slinger = False

    elif "Latest Module Build" in e.Line:
        hgx.Messages.Chat('/tell "{0}" Auto-Pilot Initialized. Chat AP Help for a list of in-game chat commands.'.format(gb_character))

        if ad_auto_damage:
            autoDamage_updatePlayer()

if __name__ == "__main__":
    hgx.GameEvents.LogEntryRead += on_logread