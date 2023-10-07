import subprocess


def execute_script(script):
    response = {'status': False, 'message': 'NOT INITIALIZED'}
    try:
        # Run the Bash script
        subprocess.run(['bash', script], check=True)
        response['status'] = True
        response['message'] = f"{script} Executed"
    except subprocess.CalledProcessError as e:
        response['message'] = f"{e}"

    return response
