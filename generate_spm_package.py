import os
import shutil
import urllib.request
import zipfile
import re
from pathlib import Path
from collections import defaultdict

# Configuration
UPSTREAM_REPO = "https://github.com/microsoft/fluentui-emoji/archive/refs/heads/main.zip"
OUTPUT_DIR = "fluentui-emoji-swift"
ASSETS_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji/Resources"
SOURCES_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji"
PACKAGE_SWIFT = f"{OUTPUT_DIR}/Package.swift"
SWIFT_FILE = f"{SOURCES_DIR}/FluentUIEmoji.swift"
TESTS_DIR = f"{OUTPUT_DIR}/Tests/FluentUIEmojiTests"

# Prepositions that should not be capitalized in display names
PREPOSITIONS = {'of', 'the', 'in', 'on', 'at', 'by',
                'for', 'with', 'to', 'from', 'and', 'or', 'but'}


def standardize_filename(filename):
    """Convert filename to standard format: lowercase letters, numbers, underscores only."""
    # Remove file extension
    name = filename.replace('.png', '').replace('_3d', '')
    # Convert to lowercase and replace non-alphanumeric characters with underscores
    name = re.sub(r'[^a-z0-9_]', '_', name.lower())
    # Remove multiple consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name


def generate_display_name(standardized_name):
    """Generate display name from standardized filename."""
    words = standardized_name.split('_')
    display_words = []

    for i, word in enumerate(words):
        if i == 0:  # First word is always capitalized
            display_words.append(word.capitalize())
        elif word.lower() in PREPOSITIONS:  # Prepositions remain lowercase
            display_words.append(word.lower())
        else:
            display_words.append(word.capitalize())

    return ' '.join(display_words)


def to_camel_case(name):
    """Convert a string like 'Grinning Face' to 'grinningFace'."""
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).split()
    if not words:
        return name.lower()
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def categorize_emoji(name):
    """Categorize emoji based on simplified name patterns."""
    name_lower = name.lower()

    # Faces & Emotions (strictly facial expressions)
    face_keywords = ['face', 'smile', 'grin', 'laugh', 'cry', 'tear', 'wink', 'kiss', 'angry', 'sad',
                     'happy', 'emotion', 'feeling', 'joy', 'sorrow', 'surprised', 'shocked', 'nervous',
                     'worried', 'confused', 'sleepy', 'tired', 'frown', 'pout', 'smirk', 'expressionless',
                     'neutral', 'unamused', 'relieved', 'pensive', 'astonished', 'hushed',
                     'flushed', 'pleading', 'grimacing', 'lying', 'shushing', 'thinking', 'zipper']
    # Exclude non-face items that might contain these keywords
    if any(keyword in name_lower for keyword in face_keywords) and not any(exclude in name_lower for exclude in ['cat', 'monkey', 'moon', 'sun']):
        return 'faces'

    # Time & Numbers (clocks, numbers, calendars)
    time_keywords = ['clock', 'oclock', 'thirty', 'calendar', 'timer', 'stopwatch', 'hourglass', 'alarm',
                     'keycap', 'spiral calendar', 'tear off calendar', 'mantelpiece clock']
    if any(keyword in name_lower for keyword in time_keywords):
        return 'time'

    # People & Body
    people_keywords = ['person', 'man', 'woman', 'boy', 'girl', 'baby', 'child', 'adult', 'old',
                       'hand', 'finger', 'thumb', 'fist', 'palm', 'wave', 'clap', 'point', 'peace',
                       'ok', 'victory', 'love', 'gesture', 'body', 'head', 'hair', 'beard', 'wrestling',
                       'fencing', 'genie', 'zombie', 'bunny ears', 'with bunny ears', 'handshake',
                       'hugging', 'bust', 'busts', 'speaking head', 'brain', 'tongue', 'tooth', 'eye', 'eyes',
                       'ear', 'nose', 'mouth', 'lips', 'kiss mark', 'footprints', 'paw prints']
    if any(keyword in name_lower for keyword in people_keywords):
        return 'people'

    # Weather & Sky
    weather_keywords = ['weather', 'sun', 'moon', 'star', 'cloud', 'rain', 'snow', 'wind', 'lightning',
                        'rainbow', 'comet', 'shooting star', 'milky way', 'ringed planet', 'tornado',
                        'cyclone', 'fog', 'foggy', 'droplet', 'sweat droplets', 'umbrella', 'sunrise',
                        'sunset', 'bridge at night', 'night with stars', 'crescent', 'waxing', 'waning',
                        'gibbous', 'quarter', 'new moon', 'full moon', 'first quarter', 'last quarter']
    if any(keyword in name_lower for keyword in weather_keywords):
        return 'weather'

    # Animals & Nature
    animal_keywords = ['cat', 'dog', 'bird', 'fish', 'bear', 'pig', 'cow', 'horse', 'monkey', 'lion',
                       'tiger', 'elephant', 'mouse', 'rabbit', 'fox', 'wolf', 'frog', 'snake', 'dragon',
                       'turtle', 'whale', 'dolphin', 'shark', 'octopus', 'butterfly', 'bee', 'spider',
                       'ant', 'bug', 'tree', 'flower', 'plant', 'leaf', 'mushroom', 'nature', 'forest',
                       'chick', 'rooster', 'chicken', 'turkey', 'duck', 'eagle', 'owl', 'bat', 'koala',
                       'panda', 'penguin', 'polar bear', 'sloth', 'otter', 'beaver', 'skunk', 'raccoon',
                       'chipmunk', 'hedgehog', 'unicorn', 'zebra', 'giraffe', 'hippopotamus', 'rhinoceros',
                       'gorilla', 'orangutan', 'kangaroo', 'llama', 'camel', 'bison', 'ox', 'water buffalo',
                       'goat', 'ram', 'sheep', 'ewe', 'deer', 'moose', 'boar', 'leopard', 'seal', 'lobster',
                       'crab', 'shrimp', 'squid', 'snail', 'worm', 'microbe', 'coral', 'seedling', 'herb',
                       'shamrock', 'clover', 'palm tree', 'cactus', 'tulip', 'rose', 'sunflower', 'blossom',
                       'cherry blossom', 'hibiscus', 'lotus', 'bouquet', 'wilted flower', 'hyacinth']
    if any(keyword in name_lower for keyword in animal_keywords):
        return 'animals'

    # Food & Drink
    food_keywords = ['food', 'drink', 'coffee', 'tea', 'wine', 'beer', 'cake', 'bread', 'pizza',
                     'burger', 'fruit', 'apple', 'banana', 'grape', 'strawberry', 'cherry', 'peach',
                     'lemon', 'watermelon', 'pineapple', 'coconut', 'avocado', 'tomato', 'carrot',
                     'corn', 'potato', 'cheese', 'meat', 'chicken', 'egg', 'milk', 'honey',
                     'salt', 'pepper', 'ice cream', 'restaurant', 'kitchen', 'cooking', 'sandwich',
                     'hamburger', 'hot dog', 'taco', 'burrito', 'pizza', 'spaghetti', 'curry',
                     'sushi', 'bento', 'rice', 'noodles', 'soup', 'salad', 'pancakes', 'waffle',
                     'cookie', 'doughnut', 'pie', 'chocolate', 'candy', 'lollipop', 'custard',
                     'pudding', 'shortcake', 'cupcake', 'birthday cake', 'pretzel', 'bagel',
                     'croissant', 'baguette', 'flatbread', 'stuffed flatbread', 'tamale', 'falafel',
                     'fondue', 'dumpling', 'fortune cookie', 'takeout', 'beverage', 'tropical drink',
                     'cocktail', 'wine glass', 'beer mug', 'clinking', 'cup', 'teacup', 'hot beverage',
                     'bottle', 'sake', 'champagne', 'popping cork', 'olive', 'pickle', 'popcorn',
                     'chestnut', 'peanuts', 'beans', 'pea pod', 'garlic', 'onion', 'bell pepper',
                     'hot pepper', 'cucumber', 'leafy green', 'broccoli', 'eggplant', 'lime',
                     'kiwi fruit', 'mango', 'melon', 'blueberries', 'grapes', 'tangerine', 'pear',
                     'ginger root', 'butter', 'bacon', 'cut of meat', 'poultry leg', 'meat on bone',
                     'fried shrimp', 'fish cake', 'moon cake', 'dango', 'oden', 'roasted sweet potato',
                     'canned food', 'honey pot', 'baby bottle', 'glass of milk', 'mate', 'bubble tea']
    if any(keyword in name_lower for keyword in food_keywords):
        return 'food'

    # Activities & Sports
    activity_keywords = ['sport', 'ball', 'game', 'play', 'run', 'swim', 'ski', 'bike', 'exercise',
                         'fitness', 'gym', 'dance', 'music', 'guitar', 'piano', 'drum', 'sing',
                         'party', 'celebration', 'festival', 'concert', 'theater', 'movie', 'tv',
                         'soccer', 'football', 'basketball', 'baseball', 'tennis', 'volleyball',
                         'rugby', 'cricket', 'field hockey', 'ice hockey', 'lacrosse', 'badminton',
                         'ping pong', 'bowling', 'boxing', 'martial arts', 'wrestling', 'fencing',
                         'goal net', 'trophy', 'medal', 'sports medal', 'military medal', 'skiing',
                         'skis', 'ice skate', 'roller skate', 'skateboard', 'flying disc', 'kite',
                         'yo yo', 'chess', 'game die', 'slot machine', 'video game', 'joystick',
                         'puzzle piece', 'mahjong', 'flower playing cards', 'performing arts',
                         'circus tent', 'ferris wheel', 'roller coaster', 'carousel horse', 'trumpet',
                         'saxophone', 'violin', 'banjo', 'accordion', 'flute', 'drum', 'long drum',
                         'musical note', 'musical notes', 'musical score', 'musical keyboard',
                         'microphone', 'studio microphone', 'headphone', 'radio', 'ticket',
                         'admission tickets', 'clapper board', 'film', 'movie camera', 'video camera',
                         'film projector', 'television', 'camping', 'tent']
    if any(keyword in name_lower for keyword in activity_keywords):
        return 'activities'

    # Travel & Places
    travel_keywords = ['house', 'building', 'city', 'country', 'map', 'hotel', 'school', 'hospital',
                       'church', 'castle', 'bridge', 'tower', 'mountain', 'beach', 'desert', 'island',
                       'car', 'plane', 'train', 'boat', 'ship', 'rocket', 'bus', 'taxi', 'bicycle',
                       'road', 'street', 'park', 'garden', 'office', 'shop', 'store', 'market',
                       'mosque', 'temple', 'synagogue', 'kaaba', 'shinto shrine', 'hindu temple',
                       'classical building', 'statue of liberty', 'tokyo tower', 'mount fuji',
                       'volcano', 'national park', 'cityscape', 'houses', 'derelict house',
                       'house with garden', 'love hotel', 'convenience store', 'department store',
                       'post office', 'japanese post office', 'bank', 'atm', 'customs', 'passport control',
                       'baggage claim', 'left luggage', 'elevator', 'escalator', 'wheelchair symbol',
                       'mens room', 'womens room', 'restroom', 'water closet', 'potable water',
                       'non potable water', 'litter in bin sign', 'no littering', 'no smoking',
                       'no entry', 'prohibited', 'children crossing', 'no pedestrians', 'no bicycles',
                       'no mobile phones', 'no one under eighteen', 'automobile', 'oncoming automobile',
                       'sport utility vehicle', 'pickup truck', 'delivery truck', 'articulated lorry',
                       'tractor', 'racing car', 'motorcycle', 'motor scooter', 'auto rickshaw',
                       'bicycle', 'kick scooter', 'bus', 'oncoming bus', 'trolleybus', 'minibus',
                       'ambulance', 'fire engine', 'police car', 'oncoming police car', 'taxi',
                       'oncoming taxi', 'airplane', 'small airplane', 'airplane departure',
                       'airplane arrival', 'helicopter', 'suspension railway', 'mountain railway',
                       'mountain cableway', 'aerial tramway', 'ship', 'motor boat', 'speedboat',
                       'ferry', 'passenger ship', 'anchor', 'sailboat', 'canoe', 'flying saucer',
                       'seat', 'luggage', 'railway car', 'high speed train', 'bullet train',
                       'train', 'metro', 'light rail', 'station', 'tram', 'monorail',
                       'railway track', 'motorway', 'construction', 'building construction',
                       'fountain', 'playground slide', 'oil drum', 'fuel pump']
    if any(keyword in name_lower for keyword in travel_keywords):
        return 'travel'

    # Symbols & Flags (symbols, signs, arrows, geometric shapes)
    symbol_keywords = ['symbol', 'sign', 'arrow', 'cross', 'circle', 'square', 'triangle', 'diamond',
                       'button', 'mark', 'warning', 'info', 'question', 'exclamation', 'check', 'x',
                       'plus', 'minus', 'multiply', 'divide', 'equals', 'infinity', 'heart', 'star',
                       'sparkle', 'sparkles', 'glowing star', 'shooting star', 'eight pointed star',
                       'six pointed star', 'star of david', 'dotted six pointed star', 'sparkler',
                       'fireworks', 'red heart', 'orange heart', 'yellow heart', 'green heart',
                       'blue heart', 'purple heart', 'brown heart', 'black heart', 'grey heart',
                       'white heart', 'pink heart', 'light blue heart', 'heart with arrow',
                       'heart with ribbon', 'sparkling heart', 'growing heart', 'beating heart',
                       'revolving hearts', 'two hearts', 'heart decoration', 'heart exclamation',
                       'broken heart', 'heart on fire', 'mending heart', 'red circle', 'orange circle',
                       'yellow circle', 'green circle', 'blue circle', 'purple circle', 'brown circle',
                       'black circle', 'white circle', 'red square', 'orange square', 'yellow square',
                       'green square', 'blue square', 'purple square', 'brown square', 'black square',
                       'white square', 'large orange diamond', 'large blue diamond', 'small orange diamond',
                       'small blue diamond', 'red triangle', 'red triangle pointed down', 'diamond with a dot',
                       'radio button', 'white square button', 'black square button', 'check box with check',
                       'ballot box with ballot', 'heavy check mark', 'heavy multiplication x', 'cross mark',
                       'cross mark button', 'heavy plus sign', 'heavy minus sign', 'heavy division sign',
                       'curly loop', 'double curly loop', 'part alternation mark', 'eight spoked asterisk',
                       'sparkle', 'double exclamation mark', 'interrobang', 'question mark', 'white question mark',
                       'red question mark', 'exclamation mark', 'white exclamation mark', 'red exclamation mark',
                       'wavy dash', 'copyright', 'registered', 'trade mark', 'hash', 'keycap asterisk',
                       'information', 'id', 'name badge', 'japanese symbol for beginner', 'heavy dollar sign',
                       'currency exchange', 'medical symbol', 'recycling symbol', 'fleur de lis', 'trident emblem',
                       'beginner', 'o button', 'p button', 'a button', 'b button', 'ab button',
                       'cl button', 'cool button', 'free button', 'id button', 'new button', 'ng button',
                       'ok button', 'sos button', 'up button', 'vs button', 'japanese', 'accept', 'congratulations', 'secret',
                       'red circle', 'blue circle', 'white circle', 'black circle',
                       'hollow red circle', 'heavy large circle', 'aries', 'taurus', 'gemini', 'cancer',
                       'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces',
                       'ophiuchus', 'six pointed star', 'atm sign', 'put litter in its place', 'potable water',
                       'wheelchair', 'no entry', 'no entry sign', 'prohibited', 'no bicycles', 'no smoking',
                       'no littering', 'non potable water', 'no pedestrians', 'children crossing',
                       'no mobile phones', 'no one under eighteen', 'radioactive', 'biohazard', 'up arrow',
                       'upper right arrow', 'right arrow', 'lower right arrow', 'down arrow', 'lower left arrow',
                       'left arrow', 'upper left arrow', 'up down arrow', 'left right arrow', 'clockwise vertical arrows',
                       'counterclockwise arrows button', 'back arrow', 'end arrow', 'on arrow', 'soon arrow',
                       'top arrow', 'twisted rightwards arrows', 'repeat button', 'repeat single button',
                       'arrow forward', 'fast forward button', 'next track button', 'play or pause button',
                       'reverse button', 'fast reverse button', 'last track button', 'upwards button',
                       'fast up button', 'downwards button', 'fast down button', 'pause button', 'stop button',
                       'record button', 'eject button', 'cinema', 'dim button', 'bright button', 'antenna bars',
                       'vibration mode', 'mobile phone off', 'female sign', 'male sign', 'transgender symbol',
                       'heavy multiplication x', 'heavy plus sign', 'heavy minus sign', 'heavy division sign',
                       'heavy equals sign', 'infinity', 'bangbang', 'interrobang', 'question', 'grey question',
                       'white question', 'grey exclamation', 'exclamation', 'heavy exclamation mark', 'flag']
    if any(keyword in name_lower for keyword in symbol_keywords):
        return 'symbols'

    # Objects & Tools (default)
    object_keywords = ['phone', 'computer', 'book', 'pen', 'key', 'lock', 'tool', 'hammer', 'knife',
                       'money', 'coin', 'gem', 'ring', 'crown', 'hat', 'shirt', 'dress', 'shoe', 'bag',
                       'watch', 'glasses', 'light', 'fire', 'water', 'briefcase', 'handbag', 'purse',
                       'clutch bag', 'backpack', 'luggage', 'suitcase', 'shopping bag', 'shopping cart',
                       'basket', 'gift', 'wrapped gift', 'ribbon', 'bow', 'balloon', 'confetti',
                       'party popper', 'scissors', 'wrench', 'screwdriver', 'nut and bolt', 'gear',
                       'brick', 'magnet', 'gun', 'pistol', 'bomb', 'firecracker', 'knife', 'dagger',
                       'sword', 'shield', 'bow and arrow', 'boomerang', 'mirror', 'lipstick',
                       'gem stone', 'crown', 'top hat', 'graduation cap', 'billed cap', 'womans hat',
                       'rescue workers helmet', 'military helmet', 'prayer beads', 'lipstick', 'ring',
                       'handbag', 'purse', 'clutch bag', 'school backpack', 'briefcase', 'necktie',
                       'jeans', 'dress', 'bikini', 'one piece swimsuit', 'kimono', 'sari', 'lab coat',
                       'safety vest', 'coat', 'shorts', 'gloves', 'scarf', 'socks', 'running shoe',
                       'hiking boot', 'womans boot', 'mans shoe', 'high heeled shoe', 'womans sandal',
                       'thong sandal', 'ballet shoes', 'flat shoe', 'running shirt', 'martial arts uniform']
    if any(keyword in name_lower for keyword in object_keywords):
        return 'objects'

    # Default to objects
    return 'objects'


def generate_search_tags(name):
    """Generate simplified search tags from emoji name only."""
    name_lower = name.lower()
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_lower).split()
    # Only use words from the name, no synonyms
    return sorted(list(set(words)))


def download_and_extract_repo():
    """Download and extract the upstream fluentui-emoji repository."""
    print("Downloading fluentui-emoji repository...")
    urllib.request.urlretrieve(UPSTREAM_REPO, "fluentui-emoji.zip")
    with zipfile.ZipFile("fluentui-emoji.zip", "r") as zip_ref:
        zip_ref.extractall("temp")
    os.remove("fluentui-emoji.zip")
    return "temp/fluentui-emoji-main"


def create_package_structure():
    """Create the SPM package directory structure."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(SOURCES_DIR, exist_ok=True)
    os.makedirs(TESTS_DIR, exist_ok=True)


def copy_emoji_assets(repo_dir):
    """Copy 3D PNG assets to Resources/ and standardize filenames."""
    assets_path = f"{repo_dir}/assets"
    copied_files = 0
    filename_counts = defaultdict(int)

    # First pass: collect all files and their standardized names
    files_to_copy = []
    for emoji_dir in Path(assets_path).iterdir():
        if emoji_dir.is_dir():
            for file in emoji_dir.glob("3D/*_3d.png"):
                standardized_name = standardize_filename(file.name)
                files_to_copy.append((file, standardized_name))

    # Second pass: handle duplicates and copy files
    for file, standardized_name in files_to_copy:
        filename_counts[standardized_name] += 1

        # Handle duplicates by adding suffix
        if filename_counts[standardized_name] > 1:
            final_name = f"{standardized_name}_{filename_counts[standardized_name]:02d}_3d.png"
        else:
            final_name = f"{standardized_name}_3d.png"

        dest_file = Path(ASSETS_DIR) / final_name
        shutil.copy(file, dest_file)
        print(f"Copied {file} to {dest_file}")
        copied_files += 1

    print(f"Total files copied: {copied_files}")


def generate_swift_file():
    """Generate a Swift enum with camelCase cases for each emoji based on actual files."""
    emoji_cases = []
    emoji_data = []
    generated_emojis = set()

    # Process actual files in the assets directory
    for file in Path(ASSETS_DIR).glob("*_3d.png"):
        # Get the standardized name without _3d.png
        standardized_name = file.stem.replace('_3d', '')

        # Generate display name
        display_name = generate_display_name(standardized_name)

        # Generate camelCase name
        camel_name = to_camel_case(display_name)

        # Ensure valid Swift identifier
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', camel_name):
            camel_name = f"_{camel_name}"

        # Handle duplicate camelCase names
        original_camel_name = camel_name
        counter = 1
        while camel_name in generated_emojis:
            camel_name = f"{original_camel_name}_{counter:02d}"
            counter += 1

        emoji_cases.append((camel_name, standardized_name))
        emoji_data.append({
            'camel_name': camel_name,
            'display_name': display_name,
            'standardized_name': standardized_name,
            'category': categorize_emoji(display_name),
            'search_tags': generate_search_tags(display_name)
        })
        generated_emojis.add(camel_name)
        print(
            f"Generated emoji: {camel_name} -> {standardized_name}_3d.png (Display: {display_name})")

    # Log the number of generated cases for debugging
    print(f"Generated {len(emoji_cases)} emoji cases")

    cases = "\n    ".join(
        f'case {name} = "{identifier}"' for name, identifier in emoji_cases)

    # Generate search tag mappings with commas
    search_mappings = []
    for data in emoji_data:
        tags_str = ', '.join(f'"{tag}"' for tag in data['search_tags'])
        search_mappings.append(f'        .{data["camel_name"]}: [{tags_str}]')

    # Define popular emojis, only including those that exist in generated_emojis
    candidate_popular_emojis = [
        'grinningFace', 'smilingFaceWithHeartEyes', 'winkingFace', 'thumbsUp', 'redHeart'
    ]
    popular_emojis = [
        f'.{camel_name}' for camel_name in candidate_popular_emojis if camel_name in generated_emojis]
    if not popular_emojis:
        # Fallback to first few emojis if none of the candidates exist
        popular_emojis = [f'.{data["camel_name"]}' for data in emoji_data[:5]]
    popular_emojis_code = ', '.join(popular_emojis)
    print(f"Popular emojis included: {popular_emojis}")

    swift_content = f"""
// FluentUIEmoji.swift
// Generated automatically by generate_spm_package.py

import Foundation

public enum FluentUIEmoji: String, CaseIterable {{
    {cases}

    /// Returns the camelCase identifier for the emoji (same as case name).
    public var identifier: String {{
        return self.rawValue
    }}
    
    /// Returns the human-readable display name for the emoji.
    public var displayName: String {{
        // Convert standardized name to display name
        let words = self.rawValue.split(separator: "_").map(String.init)
        var displayWords: [String] = []
        
        for (index, word) in words.enumerated() {{
            if index == 0 {{
                displayWords.append(word.capitalized)
            }} else if ["of", "the", "in", "on", "at", "by", "for", "with", "to", "from", "and", "or", "but"].contains(word.lowercased()) {{
                displayWords.append(word.lowercased())
            }} else {{
                displayWords.append(word.capitalized)
            }}
        }}
        
        return displayWords.joined(separator: " ")
    }}

    /// Returns the URL for the emoji's 3D PNG asset.
    public var url: URL? {{
        // Use the standardized name directly
        let fileName = self.rawValue + "_3d"
        
        if let url = Bundle.module.url(forResource: fileName, withExtension: "png") {{
            return url
        }}
        return nil
    }}
    
    /// Returns the category of the emoji.
    public var category: EmojiCategory {{
        switch self {{
{_generate_category_switch_cases(emoji_data)}
        }}
    }}
    
    /// Returns search tags for the emoji.
    public var searchTags: [String] {{
        return Self.searchTagsMap[self] ?? []
    }}
    
    /// Map of emojis to their search tags.
    private static let searchTagsMap: [FluentUIEmoji: [String]] = [
{',\n'.join(search_mappings)}
    ]
    
    /// Returns emojis in the specified category.
    public static func emojis(in category: EmojiCategory) -> [FluentUIEmoji] {{
        return allCases.filter {{ $0.category == category }}
    }}
    
    /// Returns a list of popular emojis for quick access.
    public static let popular: [FluentUIEmoji] = [
        {popular_emojis_code}
    ].compactMap {{ emoji in
        // Only include if the emoji actually exists in our cases
        return allCases.contains(emoji) ? emoji : nil
    }}
    
    /// Search emojis by text query.
    public static func search(_ query: String) -> [FluentUIEmoji] {{
        let lowercaseQuery = query.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        guard !lowercaseQuery.isEmpty else {{ return [] }}
        
        return allCases.filter {{ emoji in
            // Check display name
            if emoji.displayName.lowercased().contains(lowercaseQuery) {{
                return true
            }}
            
            // Check search tags
            return emoji.searchTags.contains {{ tag in
                tag.lowercased().contains(lowercaseQuery)
            }}
        }}
    }}
}}

/// Categories for organizing emojis.
public enum EmojiCategory: String, CaseIterable {{
    case faces = "Faces & Emotions"
    case people = "People & Body"
    case time = "Time & Numbers"
    case animals = "Animals & Nature"
    case weather = "Weather & Sky"
    case food = "Food & Drink"
    case activities = "Activities & Sports"
    case travel = "Travel & Places"
    case objects = "Objects & Tools"
    case symbols = "Symbols & Flags"
    
    /// Display name for the category.
    public var displayName: String {{
        return self.rawValue
    }}
    
    /// English name for the category.
    public var englishName: String {{
        switch self {{
        case .faces: return "Faces and Emotions"
        case .people: return "People and Body"
        case .time: return "Time and Numbers"
        case .animals: return "Animals and Nature"
        case .weather: return "Weather and Sky"
        case .food: return "Food and Drink"
        case .activities: return "Activities and Sports"
        case .travel: return "Travel and Places"
        case .objects: return "Objects and Tools"
        case .symbols: return "Symbols and Flags"
        }}
    }}
    
    /// Icon emoji for the category.
    public var icon: String {{
        switch self {{
        case .faces: return "😀"
        case .people: return "👤"
        case .time: return "🕐"
        case .animals: return "🐶"
        case .weather: return "☀️"
        case .food: return "🍎"
        case .activities: return "⚽"
        case .travel: return "🏠"
        case .objects: return "📱"
        case .symbols: return "⭐"
        }}
    }}
}}
"""

    with open(SWIFT_FILE, "w") as f:
        f.write(swift_content)


def _generate_category_switch_cases(emoji_data):
    """Generate switch cases for category mapping."""
    category_groups = {}
    for data in emoji_data:
        category = data['category']
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(data['camel_name'])

    cases = []
    for category, emojis in category_groups.items():
        emoji_list = ', '.join(f'.{emoji}' for emoji in emojis)
        cases.append(
            f'        case {emoji_list}:\n            return .{category}')

    return '\n'.join(cases)


def generate_package_swift():
    """Generate the Package.swift file for the SPM package."""
    package_content = """
// swift-tools-version:5.5
// Generated automatically by generate_spm_package.py

import PackageDescription

let package = Package(
    name: "FluentUIEmoji",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15)
    ],
    products: [
        .library(
            name: "FluentUIEmoji",
            targets: ["FluentUIEmoji"]
        ),
    ],
    targets: [
        .target(
            name: "FluentUIEmoji",
            path: "Sources/FluentUIEmoji",
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "FluentUIEmojiTests",
            dependencies: ["FluentUIEmoji"]
        )
    ]
)
"""
    with open(PACKAGE_SWIFT, "w") as f:
        f.write(package_content)


def generate_test_file():
    """Generate a basic test file for the SPM package."""
    test_content = r"""
// FluentUIEmojiTests.swift
// Generated automatically by generate_spm_package.py

import XCTest
@testable import FluentUIEmoji

final class FluentUIEmojiTests: XCTestCase {
    func testEmojiURLs() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertNotNil(emoji.url, "URL for \(emoji.displayName) should not be nil")
        }
    }
    
    func testEmojiIdentifiers() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertFalse(emoji.identifier.isEmpty, "Identifier should not be empty")
            XCTAssertEqual(emoji.identifier, emoji.rawValue, "Identifier should match rawValue")
        }
    }
    
    func testEmojiDisplayNames() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertFalse(emoji.displayName.isEmpty, "Display name should not be empty")
        }
    }
    
    func testEmojiCategories() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertTrue(EmojiCategory.allCases.contains(emoji.category), "Category should be valid")
        }
    }
    
    func testSearchFunctionality() {
        let results = FluentUIEmoji.search("face")
        XCTAssertFalse(results.isEmpty, "Search for 'face' should return results")
        
        let emptyResults = FluentUIEmoji.search("")
        XCTAssertTrue(emptyResults.isEmpty, "Empty search should return no results")
    }
    
    func testPopularEmojis() {
        XCTAssertFalse(FluentUIEmoji.popular.isEmpty, "Popular emojis list should not be empty")
        for emoji in FluentUIEmoji.popular {
            XCTAssertTrue(FluentUIEmoji.allCases.contains(emoji), "Popular emoji should exist in allCases")
        }
    }
    
    func testCategoryFiltering() {
        for category in EmojiCategory.allCases {
            let emojis = FluentUIEmoji.emojis(in: category)
            for emoji in emojis {
                XCTAssertEqual(emoji.category, category, "Emoji should belong to correct category")
            }
        }
    }
    
    func testFilenameStandardization() {
        // Test that all emojis have valid URLs
        for emoji in FluentUIEmoji.allCases {
            XCTAssertNotNil(emoji.url, "Emoji \(emoji.rawValue) should have a valid URL")
        }
    }
    
    func testCategoryDistribution() {
        // Test that each category has at least one emoji
        for category in EmojiCategory.allCases {
            let emojisInCategory = FluentUIEmoji.emojis(in: category)
            XCTAssertFalse(emojisInCategory.isEmpty, "Category \(category.displayName) should not be empty")
        }
    }
}
"""
    with open(f"{TESTS_DIR}/FluentUIEmojiTests.swift", "w") as f:
        f.write(test_content)


def main():
    """Main function to generate the SPM package."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists("temp"):
        shutil.rmtree("temp")

    repo_dir = download_and_extract_repo()
    create_package_structure()
    copy_emoji_assets(repo_dir)
    generate_swift_file()
    generate_package_swift()
    generate_test_file()

    shutil.rmtree("temp")
    print(f"SPM package generated at {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
