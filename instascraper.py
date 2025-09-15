import os
import random
import instaloader
import re

meme_accounts = [
    "9gag",
    "thefatjewish",
    "fuckjerry",
    "tank.sinatra",
    "memezar",
    "epicfunnypage",
    "memequeeninc",
    "thearchbish0pofbanterbury",
    "sarcasm_only",
    "thefunnyintrovert",
    "meme.w0rld",
    "ladbible",
    "pubity",
    "hoodclips",
    "daquan",
    "funnymemes",
    "middleclassfancy",
    "mytherapistsays",
    "officialseanpenn",
    "memes",
    "shitheadsteve",
    "thecommentsection",
    "thecovltnation",
    "everysingletime",
    "meme.economy",
    "joebuddenmemes",
    "thesavagery",
    "couplesnote",
    "kalesalad",
    "shitpostgateway",
    "betches",
    "failedtrips",
    "funnypeoplearefun",
    "5.min.crafts.memes",
    "juniorhumor",
    "browns_planet",
    "boredpanda",
    "thefunniestpage",
    "memesaredecent",
    "comicarchive",
    "grapejuiceboys",
    "whitepeoplehumor",
    "insta.comedy",
    "viralaccounts",
    "tmwbuddy",
    "scoobydoofruitsnacks",
    "realtalkingfish",
    "memescollect",
    "seabusmemes",
    "lmao.gaming",
    "yourlordandsaviourrealjesus",
    "meme.storiez",
    "epic.cattos",
    "solid__snack",
    "yourlordandsaviourpeejesus",
    "softcatmemes",
    "ngmgame",
    "the_cloudy_one_ig",
    "memebonkers",
    "elmemeplug",
    "memesnetworks",
    "thelittlestmemes",
    "memedazzler",
    "thememelingo",
    "nowherelad",
    "huge.chad",
    "rubii.meme",
    "peggle.master",
    "blood_of_a_simp",
    "cheese_boy11",
    "the_bromantic",
    "drunkpeopledoingthings",
    "casinohive",
    "citadel.sugma",
    "opium.ballin",
    "brainrot.memezy",
    "negusflex",
    "ron.mcheehee",
    "supermonkeycherrim",
    "fxckslately",
    "no_juv",
    "heardszn",
    "lil_.memer",
    "2wannabememes",
    "l0wqualitymemes",
    "shit.post_central_",
    "soggy_milk151",
    "sbcarcontent",
    "the_memeland_limited",
    "your_skydaddy",
    "prolificmemes",
    "scoopsenseai",
    "horrendous.memes",
    "highlyrelatablememe",
    "tvshowsargeant",
    "negrosaki_reels",
    "cllix.lol",
    "landerr.exe",
    "lobsterpoptart",
    "memee.app",
    "orbismala",
    "sigma.shitpostin",
    "baltimites",
    "osenperez",
    "ofnjt_",
    "catdingaling",
    "shitpostop0",
    "wasted",
    "chiggagrinch",
    "mua.___.249",
    "imdrip",
    "punishrek",
    "koromtable",
    "uncrustable.memess",
    "diablo_unholy",
    "tidehush",
    "theenmemer",
    "m3ndher",
    "fwiggin_",
    "football_memories786",
    "lil_demos",
    "caffeinedestroyer",
    "negusflex",
    "love_ur_mate",
    "unorthodox_wasabi",
    "roadtobtcforblack",
    "misani.music",
    "wickster.exe",
    "theworld_we_know",
    "grandmas.butt",
    # Expand with more
]

def cleanup_scrape_directory(scrape_dir):
    """
    Removes all files (recursively) within `scrape_dir` that do NOT end with:
    .mp4, .mov, or .MOV.
    """
    valid_extensions = {'.mp4', '.mov'}  # We'll handle .MOV by lowercase check
    for root, dirs, files in os.walk(scrape_dir):
        for file in files:
            # Split file extension, compare lowercased extension to valid set
            _, ext = os.path.splitext(file)
            if ext.lower() not in valid_extensions:
                file_path = os.path.join(root, file)
                print(f"Deleting file: {file_path}")
                os.remove(file_path)

def get_suggested_username_from_comments(L, my_username="sunny_dusty_reacts"):
    """
    1. Looks at `my_username`'s most recent video post.
    2. Scans the comments for any comment that contains "react" and an "@username".
    3. If found, returns a tuple: (suggested_username, comment_author_username).
       Otherwise, returns None.
    """
    try:
        profile = instaloader.Profile.from_username(L.context, my_username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: The username '{my_username}' does not exist or is not visible.")
        return None
    except Exception as e:
        print(f"Error accessing profile '{my_username}': {e}")
        return None

    # Find the most recent video post
    recent_video_post = None
    for post in profile.get_posts():
        if post.is_video:
            recent_video_post = post
            break  # We only need the most recent video

    if not recent_video_post:
        print(f"No recent video found on your account ({my_username}).")
        return None

    print(f"Found recent video post on '{my_username}' => Shortcode: {recent_video_post.shortcode}")

    # Use a regex that finds any comment containing "react" and then an "@" followed by a username.
    pattern = re.compile(r"react.*?@(\w+)", re.IGNORECASE)

    try:
        for comment in recent_video_post.get_comments():
            match = pattern.search(comment.text)
            if match:
                suggested_username = match.group(1)
                # Attempt to get the comment author's username; this attribute is available on instaloader.Comment objects.
                comment_author = getattr(comment.owner, 'username', 'unknown')
                print(f"Found a suggested username in comments: {suggested_username} (suggested by: {comment_author})")
                return suggested_username, comment_author
    except Exception as e:
        print(f"Error while reading comments: {e}")

    print("No valid comment with 'react' and '@username' found.")
    return None

def download_latest_video_from_account(L, chosen_username, credit_text, videos_to_download=1):
    """
    Given a valid `chosen_username`, download the most recent `videos_to_download`
    videos from that account into your scrape directory, then create a credits .txt
    with the same base filename for each video (plus "_reacted" suffix), and finally clean up.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Where the videos go
    scrape_directory = os.path.join(base_dir, "scrape")
    # Where the .txt "credits" files go
    credits_directory = os.path.join(base_dir, "credits")

    if not os.path.exists(scrape_directory):
        os.makedirs(scrape_directory)

    if not os.path.exists(credits_directory):
        os.makedirs(credits_directory)

    # Attempt to get the profile
    try:
        profile = instaloader.Profile.from_username(L.context, chosen_username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Error: The username '{chosen_username}' does not exist or is not visible.")
        return
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"Error: The account '{chosen_username}' is private and not accessible.")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

    # Track how many videos we've downloaded
    videos_found = 0

    # Iterate posts (newest first)
    for post in profile.get_posts():
        if post.is_video:
            try:
                # Download the post (video + metadata) to scrape_directory\<chosen_username>
                # Because filename_pattern = "{shortcode}", the MP4 will be named "<shortcode>.mp4"
                L.download_post(post, target=profile.username)
                videos_found += 1
                print(f"Downloaded video from post: {post.shortcode}")

                # The base filename is simply the shortcode (since Instaloader saves e.g. "ABCDE123.mp4")
                base_name = post.shortcode
                # Credits file => "<shortcode>_reacted.txt"
                credit_filename = f"{base_name}_reacted.txt"
                credit_file_path = os.path.join(credits_directory, credit_filename)

                # Write the credit text to that file
                with open(credit_file_path, "w", encoding="utf-8") as f:
                    f.write(credit_text)

            except Exception as e:
                print(f"Failed to download post {post.shortcode}: {e}")

            # If we've downloaded the desired number of videos, break
            if videos_found >= videos_to_download:
                break

    if videos_found == 0:
        print(f"No recent video found on the account: {chosen_username}")
    else:
        print(f"\nFinished downloading {videos_found} video(s) from '{chosen_username}'.")

    # Cleanup the folder (remove unwanted non-.mp4/.mov files)
    cleanup_scrape_directory(scrape_directory)

def main(check=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scrape_directory = os.path.join(base_dir, "scrape")
    
    
    L = instaloader.Instaloader(
        dirname_pattern=scrape_directory,
        filename_pattern="{shortcode}",
        download_comments=False,
    )

    # credentials.txt in the same folder as this script
    credentials = {}

    with open("credentials.txt", "r") as f:
        for line in f:
            if ":" in line:  # only process valid key:value lines
                key, value = line.strip().split(":", 1)
                credentials[key] = value

    # Load Instagram credentials
    username = credentials.get("igusername")
    password = credentials.get("igpassword")

    comment_suggester = None
    if check:
        L.login(username, password)
        result = get_suggested_username_from_comments(L, my_username=username)
        if result:
            used_username, comment_suggester = result
        else:
            used_username = random.choice(meme_accounts)
    else:
        used_username = random.choice(meme_accounts)

    if comment_suggester:
        credit_text = (
            f"Content provided by: @{used_username}\n"
            f"Thank you for the reaction suggestion! @{comment_suggester}\n"
            'Leave a comment saying: "react to: @username" to have their content featured next!'
        )
    else:
        credit_text = (
            f"Content provided by: @{used_username}\n"
            'Leave a comment saying: "react to: @username" to have their content featured next!'
        )

    download_latest_video_from_account(
        L,
        chosen_username=used_username,
        credit_text=credit_text,
        videos_to_download=1
    )

if __name__ == '__main__':
    check = False
    main(check)