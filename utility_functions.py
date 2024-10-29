import numpy as np
from datetime import datetime, timezone
from os import getlogin, path, makedirs
import sys

### README
# this file contains functions to support various print commands
#
# text_options is a short dictionary for adding effects to text in terminal output
# "reset" should always be used after another text option so that output after the
# completion of the plotting program remains normal. For example:
# my_string = "i am green and underlined"
# print(text_options["green"] + text_options["uline"] + my_string + text_options["reset"])
# is a valid usage.
# INFO: \033[ is an ANSI escape sequence that usually works for Mac and Linux
# the escape sequence is followed by some number denoting an option, and terminated
# with an m. To string multiple options, see the entry for "bold_italic_blink".
# more info here: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

text_options = {
  "reset" : "\033[m",
  "bold"  : "\033[1m",
  "uline" : "\033[4m",
  "blink" : "\033[5m",
  "bold_italic_blink" : "\033[1m\033[4m\033[5m",
  "red"    : "\033[91m",
  "green"  : "\033[92m",
  "yellow" : "\033[93m",
  "purple"   : "\033[94m",
  "pink"   : "\033[95m",
}

def log_print(text, log_file, time=False, *args, **kwargs):
  # hack for simultaneous logging + terminal output
  if (time==True): time_print(text)
  else: print(text, *args, **kwargs)
  if log_file:
    if (time==True): text = datetime.now(timezone.utc).strftime('%H:%M:%S') + ' ' + text
    log_file.write(str(str(text)+'\n'))

def time_print(*args, **kwargs):
  '''
  Helper function to append a time to print statements, the idea being
  to give the user an idea of progress, bottlenecks, and total time of a computation.
  Randomly selected emojis can be added if the user enrolls themself by adding 
  their login handle to the if statement. 
  '''
  emoji = np.random.choice([";) ", ":^)", "<.<", ">.>", ":O ", "^.^", "UwU", "owO"])
  time  = datetime.now(timezone.utc).strftime('%H:%M:%S')
  if getlogin() == "ballmond":
    time = emoji + "  " + time
  print(f"{time} UTC", *args, **kwargs)


def attention(input_string, log_file):
  '''
  Helper function to print a string in a large font in a central
  position so that it cannot be missed. Blinking text can be added
  if the user enrolls themself by adding their login handle to the if statement. 
  '''
  screen_width, spacer = 76, "-"
  log_print("the final state mode is".upper().center(screen_width, spacer), log_file)
  if getlogin() == "ballmond":
    # can't use normal center function because escape characters contribute to length of string
    center_val = (screen_width - 3*len(input_string))//2
    s_1 = text_options["bold_italic_blink"] + text_options["green"]  + input_string + text_options["reset"]
    s_2 = text_options["bold_italic_blink"] + text_options["yellow"] + input_string + text_options["reset"]
    s_3 = text_options["bold_italic_blink"] + text_options["purple"] + input_string + text_options["reset"]
    s_full = center_val*" " + s_1+s_2+s_3 + center_val*" " 
    log_print(s_full, log_file)
  log_print(input_string.center(screen_width, spacer), log_file)


def make_directory(directory_name, testing=False):
  date_and_time  = datetime.now(timezone.utc).strftime('from_%d-%m_at_%H%M')
  directory_name = directory_name + "_" + date_and_time
  if testing: directory_name += "_testing"
  if not path.isdir(directory_name):
    makedirs(directory_name)
  else:
    print("WARNING: directory already exists, wait one minute.")
    sys.exit()
  return directory_name


SCREEN_WIDTH = 76
SPACER = "-"
def print_setup_info(setup):
  # how do you specify class types with pylint? 
  
  testing, final_state_mode, jet_mode, era, lumi = setup.state_info
  using_directory, plot_dir, log_file, use_NLO, file_map = setup.file_info
  hide_plots, hide_yields, DeepTau_version, do_JetFakes, semilep_mode = setup.misc_info

  screen_width, spacer = SCREEN_WIDTH, SPACER
  attention(final_state_mode, log_file)
  log_print(f"ERA = {era} \t LUMI={lumi} \t JET MODE={jet_mode} \t TESTING={testing}", log_file)
  log_print(spacer*screen_width, log_file)
  log_print(f"INPUT  DATA DIRECTORY : {using_directory}", log_file)
  log_print(f"OUTPUT PLOT DIRECTORY : {plot_dir}", log_file)
  log_print(spacer*screen_width, log_file)
  log_print("Miscellaneous info ".upper().center(screen_width, spacer), log_file)
  log_print(f"NLO samples (DY/WJ)={use_NLO} \t DeepTauVersion={DeepTau_version}", log_file)
  log_print(f"Include JetFakes={do_JetFakes} \t \t FF semileptonic mode={semilep_mode}", log_file)
  log_print(spacer*screen_width, log_file)


def print_processing_info(good_events, branches, vars_to_plot, log_file):
  screen_width, spacer = SCREEN_WIDTH, SPACER
  log_print("Good events pass initial filtering ".upper().center(screen_width, spacer), log_file)
  log_print(good_events, log_file)
  log_print('', log_file)

  log_print("Loading branches ".upper().center(screen_width, spacer), log_file)
  log_print(branches, log_file)
  log_print('', log_file)

  log_print("Going to plot these variables ".upper().center(screen_width, spacer), log_file)
  log_print(vars_to_plot, log_file)
  log_print(spacer*screen_width, log_file)


