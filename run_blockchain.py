import subprocess
import os

def run_geth():
    # Define the path to the node directory
    node_dir = "ethpoa/node0"

    # Check if the directory exists
    if not os.path.isdir(node_dir):
        print(f"The directory {node_dir} does not exist.")
        return
    
    # Change the current working directory to node_dir
    os.chdir(node_dir)

    # Define the command to run
    geth_command = [
        "geth",
        "--datadir", "./data",
        "--networkid", "999",
        "--port", "30303",
        "--http",
        "--http.port", "8545",
        "--http.corsdomain", "*",
        "--http.api", "eth,web3,personal,net,miner,admin,debug",
        "--nodiscover",
        "--allow-insecure-unlock",
        "--mine",
        "--unlock", "0xFAD0ca1973068C404aDD63eBc98A18Ff61A4E419",
        "--password", "./password.txt",
        "--miner.etherbase", "0xFAD0ca1973068C404aDD63eBc98A18Ff61A4E419",
        "--miner.gasprice", "0",
        "console"
    ]

    # Run the command
    try:
        subprocess.run(geth_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running geth: {e}")

if __name__ == "__main__":
    run_geth()
