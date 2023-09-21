"""
Download posts from list of location ID's (locationIDs.txt)
"""
import os
import instaloader

def main():
    # Define the user
    USER = ""
    
    # Read the location IDs from a file
    with open(os.getcwd()+'/locationIDs.txt', 'r') as file:
        location_ids = [line.strip() for line in file if line.strip()]

    # Load session previously saved with this username 
    L = instaloader.Instaloader(fatal_status_codes=[400, 429],
                                download_pictures=True,
                                download_comments=True, 
                                download_videos=False, 
                                download_geotags=False,
                                save_metadata=True)
    
    L.load_session_from_file(USER)

    # Set the current working directory to your desired path
    download_directory = os.getcwd()
    
    # Create a separate folder for each location ID
    for location_id in location_ids:
        location_folder = os.path.join(download_directory, location_id)
        os.makedirs(location_folder, exist_ok=True)  # Create the folder for the location ID
        
        # Set the download target to the location-specific folder
        os.chdir(location_folder)
        
        # Initialize a list to keep track of downloaded post URLs for each location
        downloaded_posts = set()  # Use a set to ensure uniqueness
        
        # Download locations using the location ID
        for post in L.get_location_posts(location_id):
            try:
                if post.url in downloaded_posts:
                    print(f"Skipping a post that has already been downloaded: {post.url}")
                    break  # Stop processing this location ID
                else:
                    downloaded_posts.add(post.url)
                    L.download_post(post, target=location_folder)
            except Exception as e:
                print(f"Error downloading post: {str(e)}")
        
        # After processing all posts for this location, continue to the next location ID
        print(f"Finished downloading for location ID: {location_id}")

if __name__:
    main()
