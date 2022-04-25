import pathlib, sys, re, typing
from fuzzywuzzy import process, fuzz

usage = f"Usage: {pathlib.Path(__file__).name} path_sources [path_sources ...] path_destination"

def sanitize(name:str, end:int=8) -> str:
	"""Remove the chuff"""
	return ' '.join(re.split(r"[^a-z0-9]", name.lower()))

def glob_path(path_source:pathlib.Path, extensions:tuple[str]) -> set[pathlib.Path]:
	"""Return a set ofvalid files in a given path with given extensions"""
	
	if path_source.is_file() and path_source.suffix.lower() in extensions:
		return set([path_source])
	
	elif path_source.is_dir():
		paths_filtered = set()
		for ext in extensions:
			paths_filtered.update(path_source.rglob(f"*{ext}"))
		return paths_filtered
	
	else:
		#print(f"Skipping {path_source}", file=sys.stderr)
		return set()


def collect_files(path_sources:typing.Iterable[pathlib.Path], ext_videos:tuple[str], ext_scripts:tuple[str]) -> tuple[set[pathlib.Path, pathlib.Path]]:
	"""Collect videos and scripts"""

	sources_videos  = set()
	sources_scripts = set()

	# First do the videos
	for path_video in path_sources:
		sources_videos.update(glob_path(path_video, ext_videos))

	# Now do the scripts
	for path_script in path_sources:
		sources_scripts.update(glob_path(path_script, ext_scripts))
		
	return (sources_videos, sources_scripts)

def match_video_to_scripts(path_video:pathlib.Path, paths_scripts:typing.Iterable[pathlib.Path], threshold:typing.Optional[int]=80) -> list[tuple[int, pathlib.Path]]:
	"""Find the best script match for a given video"""

	matches = set()
	
	for path_script in paths_scripts:
		
		# Declare victory if filenames match perfectly
		if path_video.stem.lower() == path_script.stem.lower():
			matches.add((1000, path_script))
			#break	# TODO: Allowing other matches for now
		
		# czvr skip
		#elif  path_video.stem[:3].isnumeric():
		#	continue

		# Do a fuzzy lil match
		else:
			score = fuzz.token_set_ratio(path_video.stem, path_script.stem)
			if threshold is not None and score < threshold:
				continue
			matches.add((score, path_script))
	
	return sorted(matches, key=lambda x: x[0], reverse=True)

def prompt_for_selection(path_video:pathlib.Path, matches:list[tuple[int, pathlib.Path]], listmax:int=5) -> typing.Optional[pathlib.Path]:
	"""Prompt the user to select a good match"""

	best_score, best_path = matches[0]

	print(f"\nBest match for {path_video}")
	print(f"Video:  {path_video.name}")
	print(f"Script: {best_path.name} ({best_score}%)")

	if len(matches) > 1:
		options = "[y]es, [m]ore, [s]kip, [q]uit"
	else:
		options = "[y]es, [s]kip, [q]uit"

	while True:
		choice = input(f"Sounds good? ({options}): ").strip().lower()
	
		if choice.startswith('y'):
			return best_path
		elif choice.startswith('s'):
			return None
		elif choice.startswith('q'):
			raise KeyboardInterrupt
		elif choice.startswith('m') and len(matches) > 1:
			break
	
	# 'More' was chosen.
	num_choices = min(listmax, len(matches))
	
	print(f"\nTop {num_choices} matches: for {path_video}:")
	for idx in range(num_choices):
		score, path_script = matches[idx]
		print(f"{idx+1}: {path_script.name} ({score}%)")
	
	while True:
		choice = input(f"Your selection? ([1-{num_choices}], [s]kip, [q]uit): ").strip().lower()

		if choice.isnumeric() and int(choice)-1 in range(num_choices):
			return matches[int(choice)-1][1]
		elif choice.startswith('s'):
			return None
		elif choice.startswith('q'):
			raise KeyboardInterrupt

def link_video_with_script(path_video:pathlib.Path, path_script:pathlib.Path, path_destination:pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
	"""Link a video and script pair to the destination folder"""

	link_video  = pathlib.Path(path_destination, path_video.name)
	link_script = link_video.with_suffix(path_script.suffix)

	if link_video.exists() or link_script.exists():
		raise FileExistsError("Video or script already exists in this path")

	# NOTE: pathlib.Path.link_to has been deprecated in favor of hardlink_to in Python 3.10.  I know.
	# Using link_to() for better compatibility for older Python versions
	path_video.link_to(link_video)
	path_script.link_to(link_script)

	# TODO: Cleanup if one link succeeded and the other failed?

	return (link_video, link_script)


def main(input_paths:typing.Iterable[str], input_dest:str):
	"""Find matching video and script pairs, and create hardlinks in another location"""

	# Ehh
	global success
	global failed

	counter = 0

	# Validate destination path
	path_destination = pathlib.Path(input_dest)
	if not path_destination.is_dir():
		sys.exit(f"Destination path must be an existing folder.\n{usage}")
	
	# Collect source paths
	paths_videos, paths_scripts = collect_files([pathlib.Path(f) for f in input_paths], ext_videos=(".mp4",".mkv",".wmv"), ext_scripts=(".funscript",))
	print(f"Found {len(paths_videos)} videos and {len(paths_scripts)} scripts to sort through...")

	if not paths_videos or not paths_scripts:
		return

	total_count = len(paths_videos)

	for path_video in paths_videos:

		counter += 1

		print(f"[{counter} of {total_count}] Looking...", end='\r')

		# Skip any videos already in the destination path
		if pathlib.Path(path_destination, path_video.name).exists():
#			print(f"Skipping file already matched: {path_video.name}", file=sys.stderr)
			continue

		# Match a video with a script
		matches = match_video_to_scripts(path_video, paths_scripts)
		
		if not matches:
#			print(f"No match for{path_video}", file=sys.stderr)
			continue

		print("")

		# Present the user with some options
		path_script_selected = prompt_for_selection(path_video, matches)
		if path_script_selected is None:
			print("")
			continue

		# Hardlink the video and script
		try:
			linked_video, linked_script = link_video_with_script(path_video, path_script_selected, path_destination)
		except Exception as e:
			print(f"Could not hardlink files for {path_video.name} to {path_destination}: {e}")
			failed.add(path_video)
		else:
			print(f"Linked {path_video.name} with {path_script_selected.name} to {path_destination}")
			success.add(path_video)
		
		print("")

if __name__ == "__main__":

	success = set()
	failed  = set()

	if len(sys.argv) < 3:
		sys.exit(f"Link videos and scripts in `path_sources` together into `path_destination`\n{usage}")

	try:
		main(sys.argv[1:-1], sys.argv[-1])
	except KeyboardInterrupt:
		print(f"\nLeaving early.\n{len(success)} pairs linked; {len(failed)} pairs failed.\n")
		sys.exit()
	except Exception as e:
		sys.exit(f"Exiting with error: {e}")
	
	print(f"\n{len(success)} pairs linked; {len(failed)} pairs failed.\n")