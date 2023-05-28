import subprocess


def run_command(command):
  process = subprocess.Popen(command, shell=True)
  process.wait()


if __name__ == "__main__":
  command_to_run = "python gcalendar/manage.py runserver"
  run_command(command_to_run)
