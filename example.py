from hue_controller import HueController

BRIDGE_IP = "127.0.0.0"  # REPLACE with your bridge's IP address

def main():
    hue = HueController(ip=BRIDGE_IP, api_key="pAf6Bky1x0yXXlrilqM9aI5NELmCR9bV78cV-KcP")

    hue.scenes = hue.get_scenes()
    print(hue.scenes)

if __name__ == "__main__":
    main()
