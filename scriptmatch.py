import pathlib, sys, re
from fuzzywuzzy import process, fuzz

def sanitize(name:str, end:int=8) -> str:
	"""Remove the chuff"""
	return ' '.join(re.split(r"[^a-z0-9]", name.lower()))

if __name__ == "__main__":

	if len(sys.argv) < 3:
		sys.exit(f"Link videos and scripts in `path_sources` together into `path_destination`\nUsage: {__file__} path_sources [path_sources ...] path_destination")
	
	# Check destination
	path_destination = pathlib.Path(sys.argv[-1])
	if not path_destination.is_dir():
		sys.exit(f"Destionation path must be a folder")
	
	# Collect source paths
	sources_scripts = set()
	sources_videos  = set()

	for source_path in [pathlib.Path(f) for f in sys.argv[1:-1]]:

		if source_path.is_file():
			if source_path.suffix.lower() == ".mp4":
				sources_videos.add(source_path)
			elif source_path.suffix.lower() == ".funscript":
				sources_scripts.add(source_path)

		elif source_path.is_dir():
			for f_path in source_path.rglob('*'):
				if f_path.suffix.lower() == ".mp4":
					sources_videos.add(f_path)
				elif f_path.suffix.lower() == ".funscript":
					sources_scripts.add(f_path)
		
		else:
			print(f"Skipping {source_path}", file=sys.stderr)

	print(f"Found {len(sources_videos)} videos and {len(sources_scripts)} scripts to sort through...")

	for source_video in sources_videos:

		# Skip already matched
		if pathlib.Path(path_destination, source_video.name).exists():
			continue
		
		matches = set()
		video_name = sanitize(source_video.stem)

		# Skip Czechvr
		if video_name.split()[0].isnumeric():
			continue

		for source_script in sources_scripts:

			# Exact match found
			if source_video.stem.lower() == source_script.stem.lower():
				matches.add((1000, source_script))
				break
			
			else:
				script_name = sanitize(source_script.stem)
				score = fuzz.token_set_ratio(script_name, video_name)
				matches.add((score, source_script))
			
		
		if not matches:
			continue

		best = sorted(matches, key=lambda x: x[0], reverse=True)[:5]
		score, script = best[0]

		if score > 80:

			print(f"Promising match:")
			print(source_video.name)
			print(script.name,f"({score})")

			while True:
				choice = input("Sounds good? (y/n): ").strip().lower()[0]
				if choice in ['y','n']:
					break
			
			if choice == 'y':
				link_video  = pathlib.Path(path_destination, source_video.name)
				link_script = link_video.with_suffix(source_script.suffix)
				print(f"Linking to {link_video} and {link_script}")
				source_video.link_to(link_video)
				source_script.link_to(link_script)
			
			print("Good.\n")