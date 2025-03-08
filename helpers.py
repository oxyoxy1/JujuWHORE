# helpers.py

import random

questions = [
    {"question": "Who is the main protagonist of Jujutsu Kaisen?", "answers": ["Yuji Itadori"]},
    {"question": "What is the name of the cursed spirit that Yuji swallows?", "answers": ["Sukuna", "Ryomen Sukuna"]},
    {"question": "Which grade of Jujutsu Sorcerer is Gojo Satoru?", "answers": ["Special Grade"]},
    {"question": "What is the name of the school where Yuji trains to become a Jujutsu Sorcerer?", "answers": ["Tokyo Metropolitan Magic Technical College", "Jujutsu High School", "Jujutsu Tech", "Tokyo Jujutsu Tech"]},
    {"question": "Who is the teacher of Yuji, Megumi, and Nobara?", "answers": ["Satoru Gojo", "Gojo Satoru", "Gojo"]},
    {"question": "What is the name of Megumi's signature technique?", "answers": ["10 Shadows", "Ten Shadows"]},
    {"question": "What does Sukuna's cursed technique primarily involve?", "answers": ["Domain Expansion"]},
    {"question": "Which of the following is not a character from Jujutsu Kaisen: A) Nanami Kento, B) Yuji Itadori, C) Naruto Uzumaki, D) Maki Zenin?", "answers": ["Naruto Uzumaki", "Naruto"]},
    {"question": "What is the name of the Zenin family's head?", "answers": ["Naobito Zenin", "Naobito"]},
    {"question": "Who is the only known user of the 'Limitless' cursed technique?", "answers": ["Satoru Gojo", "Gojo"]},
    {"question": "What is the cursed energy manipulation technique used by Satoru Gojo?", "answers": ["Infinity"]},
    {"question": "What is the name of Megumi's Domain Expansion?", "answers": ["Chimera Shadow Garden"]},
    {"question": "What is the full name of the character known as Nobara?", "answers": ["Nobara Kugisaki"]},
    {"question": "Which character is known for using the 'Black Flash' technique?", "answers": ["Yuji Itadori", "Nanami Kento", "Yuji", "Nanami"]},
    {"question": "What is the real name of the character commonly called 'Fushiguro'?", "answers": ["Megumi Fushiguro", "Megumi Zenin", "Zenin"]},
    {"question": "Who is the leader of the 'Jujutsu Kaisen' group of cursed users that oppose the Jujutsu Sorcerers?", "answers": ["Suguru Geto", "Geto"]},
    {"question": "What is the 'Shibuya Incident' in the Jujutsu Kaisen universe?", "answers": ["Disaster", "Terrorism"]},
    {"question": "Which character uses a cursed tool called the 'Feathered Spear'?", "answers": ["Maki Zenin", "Maki"]},
    {"question": "What is the 'Reverse Cursed Technique' that Satoru Gojo uses?", "answers": ["Healing", "Healing Ability"]},
    {"question": "What technique does Yuji use to channel cursed energy in the form of punches?", "answers": ["Black Flash", "Divergent Fist"]},
    {"question": "What is the name of the first curse that Yuta encounters in the series?", "answers": ["Rika Orimoto", "Rika"]},
    {"question": "What is the name of the Jujutsu Kaisen event that takes place every year, involving special grade curses?", "answers": ["The Exchange Event", "The Kyoto Exchange Event", "The Tokyo Exchange Event"]},
    {"question": "Who was the previous head of the Zenin Clan before Naobito Zenin?", "answers": ["Ogi Zenin"]},
    {"question": "What is the main ability of the 'Jujutsu Sorcerers' in the series?", "answers": ["Cursed Energy Manipulation"]},
    {"question": "What is the name of the technique that allows Gojo to manipulate the flow of cursed energy?", "answers": ["Six Eyes", "Limitless"]},
    {"question": "What is Yuji's main motivation for becoming a Jujutsu Sorcerer?", "answers": ["To save others", "Saving life", "Saving lives"]},
    {"question": "What is the ability of Megumi Fushiguro's technique?", "answers": ["Shikigami"]},
    {"question": "What is Maki Zenin's binding vow known as?", "answers": ["Heavenly Restriction"]},
    {"question": "Who is the most powerful Jujutsu Sorcerer known in the series?", "answers": ["Satoru Gojo"]},
    {"question": "Who is known as a 'Cursed Womb: Death Painting'?", "answers": ["Yuji", "Yuji Itadori"]},
    {"question": "What is the domain expansion of the character Mahito?", "answers": ["Self Embodiment of Perfection"]},
    {"question": "Who are the primary antagonists during the 'Shibuya Incident' arc?", "answers": ["Geto", "Suguru Geto", "Jogo", "Mahito", "Sukuna", "Hanami", "Dagon"]},
    {"question": "Who is Yuji Itadori's mentor in the Jujutsu world?", "answers": ["Satoru Gojo", "Gojo"]},
    {"question": "Which character is known for their ability to use the 'Six Eyes' technique?", "answers": ["Satoru Gojo", "Gojo"]},
    {"question": "What is the name of the curse that resides within Yuji's body?", "answers": ["Ryomen Sukuna", "Sukuna"]},
    {"question": "Who is the author of the Jujutsu Kaisen manga series?", "answers": ["Gege Akutami", "Gege"]},
    {"question": "Which of these characters is not a part of the Zenin Clan? A) Maki, B) Naobito, C) Jogo, D) Mei Mei?", "answers": ["Jogo"]},
    {"question": "What is the ultimate technique of Satoru Gojo that can easily eliminate large groups of enemies?", "answers": ["Limitless"]},
    {"question": "What is the most deadly curse in the Jujutsu Kaisen universe?", "answers": ["Ryomen Sukuna", "Sukuna"]},
    {"question": "Who is known for using the cursed technique 'Idle Transfiguration'?", "answers": ["Mahito"]},
    {"question": "What is the technique that uses cursed energy to create a barrier?", "answers": ["Veil"]},
    {"question": "Who is the teammate of Yuji Itadori?", "answers": ["Megumi Fushiguro", "Megumi", "Nobara Kugisaki", "Nobara"]},
    {"question": "What is the name of the final battle in Jujutsu Kaisen?", "answers": ["Shinjuku Showdown"]},
    {"question": "Which character has the ability to manipulate space and time?", "answers": ["Satoru Gojo", "Gojo"]},
]

# List of greedier images for the grind command
greedier_images = [
    "https://static.wikia.nocookie.net/jujutsu-kaisen/images/5/5a/Satoru_Gojo_arrives_on_the_battlefield_%28Anime%29.png/revision/latest?cb=20210226205256",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_nR92z6vx4iyhvu46isI1U1Ow255XYso9yA&s",
    "https://miro.medium.com/v2/resize:fit:1400/1*rKl56ixsC55cMAsO2aQhGQ@2x.jpeg",
    "https://staticg.sportskeeda.com/editor/2024/05/5dbc5-17159017650761-1920.jpg?w=640",
    "https://images4.alphacoders.com/133/1332281.jpeg",
    "https://platform.polygon.com/wp-content/uploads/sites/2/chorus/uploads/chorus_asset/file/24830205/GojoGetoShip.png?quality=90&strip=all&crop=9.375,0,55.3125,100",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQFYb4peK03HOzQjQJoMhkdLHxg067PTzqgtA&s",
    "https://www.dexerto.com/cdn-image/wp-content/uploads/2023/08/04/jujutsu-kaisen-season-2-satoru-gojo.jpeg?width=1200&quality=60&format=auto",
    "https://www.themarysue.com/wp-content/uploads/2023/10/Gojo-Satoru-and-Geto-Suguru-from-Jujutsu-Kaisen-Season-2.jpg?fit=1200%2C675",
    "https://beebom.com/wp-content/uploads/2024/09/Gojo-Satoru-from-Jujutsu-Kaisen.jpg?w=1250&quality=75",
    "https://static1.srcdn.com/wordpress/wp-content/uploads/2023/09/gojo-looks-dark-in-jujutsu-kaisen-s-op.jpg",
    "https://staticg.sportskeeda.com/editor/2024/09/3e9d1-17262958637084-1920.jpg"
]

def get_random_greedy_image():
    return random.choice(greedier_images)
