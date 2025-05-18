-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 04, 2025 at 01:06 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tourism_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `id` int(11) NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `location` varchar(255) NOT NULL,
  `time` time NOT NULL,
  `date` date NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `is_free` tinyint(1) DEFAULT 1,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `user_id` int(11) DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`id`, `image`, `name`, `description`, `location`, `time`, `date`, `category`, `is_free`, `status`, `user_id`, `date_created`, `date_modified`, `date_deleted`) VALUES
(1, 'uploads\\events\\20250502010843.jpg', 'T\'nalak Festival', 'Description: A vibrant celebration of culture and tradition in South Cotabato featuring street dancing, indigenous fashion shows, and exhibits showcasing the T’nalak cloth.', 'Koronadal City, South Cotabato, Philippines', '10:00:00', '2025-07-18', 'Festival', 1, 'approved', NULL, '2025-05-02 01:08:43', '2025-05-02 01:20:14', NULL),
(2, 'uploads\\events\\20250502011405.jpg', 'Tuna Festival', 'Description: The Tuna Festival is an annual celebration in General Santos City, known as the \"Tuna Capital of the Philippines.\" This week-long event honors the city\'s thriving tuna industry and rich maritime heritage. Festivities include vibrant street parades, culinary competitions, cultural shows, and various entertainment activities that showcase the city\'s pride in its tuna production.', 'General Santos City, South Cotabato, Philippines', '10:00:00', '2025-09-01', 'Festival', 1, 'approved', NULL, '2025-05-02 01:14:05', '2025-05-02 01:19:13', NULL),
(3, 'uploads\\events\\20250502011658.jpg', 'Kalilangan Festival', 'Description: A week-long celebration in General Santos City that showcases cultural shows, civic/military parades, agro-industrial fairs, sports competitions, and beauty pageants, reflecting the city\'s rich history and cultural diversity.', 'General Santos City, South Cotabato, Philippines', '08:00:00', '2025-02-20', 'Festival', 1, 'approved', NULL, '2025-05-02 01:16:58', '2025-05-02 01:20:29', NULL),
(4, 'uploads\\events\\20250502012147.jpg', 'Talakudong Festival', 'Description: A cultural festival in Tacurong City that features street dancing and parades, with participants wearing traditional headgear called \"kudong,\" symbolizing the city\'s heritage and history.', 'Tacurong City, Sultan Kudarat, Philippines', '12:00:00', '2025-09-18', 'Festival', 1, 'approved', NULL, '2025-05-02 01:21:47', NULL, NULL),
(5, 'C:/Users/Emnace/Downloads/maxresdefault.jpg', 'Hinugyaw Festival', 'Description: Celebrated in Koronadal City, this festival marks the city\'s founding anniversary with a blend of cultural dances, street parades, and various community activities that highlight the unity and diversity of its people.', 'Koronadal City, South Cotabato, Philippines', '09:00:00', '2025-01-10', 'Festival', 1, 'approved', 2, '2025-05-02 01:25:40', NULL, NULL),
(6, 'C:/Users/Emnace/Downloads/484947554_945031901045370_8107214534545233556_n.jpg', 'Bulad Festival', 'Description: The Bulad Festival is an annual celebration in Barangay Calumpang, General Santos City, honoring the community\'s rich tradition of dried fish (\"bulad\") production. The 2025 edition marked the 16th Bulad Festival, coinciding with the 34th Foundation Anniversary of Barangay Calumpang. The festival\'s theme was \"Drying Dreams, Strengthening Communities,\" reflecting the integral role of the dried fish industry in the local economy and culture.', 'Calumpang, General Santos City, Philippines', '10:00:00', '2025-03-08', 'Festival', 1, 'approved', 2, '2025-05-02 01:35:00', '2025-05-02 02:41:33', NULL),
(7, 'C:/Users/Emnace/Downloads/486672882_1185980406530807_5547013968471796374_n.jpg', 'Kamikazee Live at Kalilangan Festival', 'Description: The iconic Filipino rock band Kamikazee headlined the grand opening of the Kalilangan Festival 2025, delivering an electrifying performance that set the tone for the week-long celebration.', 'Pioneer Avenue Junction, General Santos City', '18:00:00', '2025-02-23', 'Concert', 1, 'approved', 2, '2025-05-02 01:41:32', NULL, NULL),
(8, 'C:/Users/Emnace/Downloads/images (23).jpg', 'Banda ni Kleggy Live in Koronadal', 'Description: The Filipino rock band Banda ni Kleggy will perform live at Ramon Magsaysay Memorial Colleges in Koronadal City, offering an evening of energetic music and entertainment.', 'RMMC, Koronadal City', '19:00:00', '2025-03-08', 'Concert', 1, 'approved', 2, '2025-05-02 01:52:45', '2025-05-02 02:42:28', NULL),
(9, 'C:/Users/Emnace/Downloads/download (15).jpg', ' Magpuri Music Festival Mindanao', 'Description: A worship music festival featuring bands like Victory Band, Twelve Tribes Worship, TITUS new GEN, and more.', 'Acharon Sports Complex, General Santos City', '12:00:00', '2025-06-12', 'Concert', 1, 'approved', 2, '2025-05-02 02:01:12', NULL, NULL),
(10, 'C:/Users/Emnace/Downloads/images (24).jpg', 'Dionela Live  Summer Fest 2025', 'Description: Get ready for the hottest beach event of the year as OPM sensation Dionela headlines the London Beach Resort Summer Fest 2025! Known for his hits “Marilag,” “Sining,” and “Musika,” Dionela will be joined by local artists for a night of unforgettable performances by the beach.', 'Barangay Bawing, General Santos City, South Cotabato', '18:00:00', '2025-05-17', 'Concert', 0, 'approved', 2, '2025-05-02 02:13:21', '2025-05-02 02:41:15', NULL),
(11, 'uploads\\events\\20250502023250.jpg', 'Sweet Notes Live 2025', 'Description: As part of the Halad Festival 2025 celebrations, the renowned sequencer band Sweet Notes, a real-life couple from General Santos City, delivered a captivating live performance. Their soulful renditions of classic hits, including “Faithfully” by Journey and “Breathless” by The Corrs, resonated with the audience, making the evening a memorable musical experience.', 'NDMC Grounds, Midsayap, North Cotabato, Philippines', '18:00:00', '2025-01-15', 'Concert', 1, 'approved', NULL, '2025-05-02 02:32:50', '2025-05-02 02:44:41', NULL),
(12, 'C:/Users/Emnace/Downloads/images (26).jpg', 'BINIverse Gensan', 'Description: As part of their regional tour, the P-pop girl group BINI delivered a dynamic performance during the BINIverse Gensan concert. The event attracted over 8,000 fans, known as \"Blooms,\" who gathered to witness the group\'s vibrant stage presence and musical prowess. Despite weather challenges, the concert proceeded with enthusiasm, marking a significant moment in BINI\'s tour.', 'KCC Mall , General Santos City, Philippines', '13:00:00', '2024-07-20', 'Concert', 0, 'approved', 2, '2025-05-02 02:39:29', '2025-05-02 02:45:12', NULL),
(13, 'C:/Users/Emnace/Downloads/images (27).jpg', '13th Regional Travel Fair', 'Description: A three-day event highlighting SOCCSKSARGEN\'s tourism assets, featuring B2B sessions, travel discounts, live performances, and artisan showcases.', 'SM City General Santos', '10:00:00', '2025-09-27', 'Exhibition', 1, 'approved', 2, '2025-05-02 09:50:42', NULL, NULL),
(14, 'C:/Users/Emnace/Downloads/download (16).jpg', 'Coffee Farmers Congress 2025', 'Description: A gathering of coffee farmers featuring brewing competitions, exhibits, and discussions on sustainable coffee production.', 'Greenleaf Hotel, General Santos City', '08:00:00', '2025-01-22', 'Exhibition', 1, 'approved', 2, '2025-05-02 09:58:56', '2025-05-02 10:03:23', NULL),
(15, 'C:/Users/Emnace/Downloads/448570952_481556600915448_1872575164637529907_n-600x337.jpg', 'Food and Culinary Expo', 'Description: An exhibition showcasing the region\'s culinary delights, including cooking demonstrations and food tasting.', 'Koronadal City, South Cotabato', '10:00:00', '2025-05-10', 'Exhibition', 1, 'approved', 2, '2025-05-02 10:01:50', NULL, NULL),
(16, 'C:/Users/Emnace/Downloads/images (28).jpg', 'Basketball League Finals', 'Description: The culminating event of the city\'s inter-barangay basketball league, showcasing top teams vying for the championship.', 'Kidapawan City Gymnasium', '18:00:00', '2025-06-20', 'Sports', 0, 'approved', 2, '2025-05-02 10:12:44', NULL, NULL),
(17, 'C:/Users/Emnace/Downloads/images (29).jpg', ' 2025 SRAA Meet', 'Description: A week-long multi-sport event featuring over 7,000 student-athletes from the region\'s nine school divisions, serving as a qualifier for the Palarong Pambansa.', 'South Cotabato Sports Complex, Koronadal City', '08:00:00', '2025-03-03', 'Sports', 1, 'approved', 2, '2025-05-02 10:15:29', NULL, NULL),
(18, 'C:/Users/Emnace/Downloads/SarBay+volleyball+showdown+in+Gumasa.jpg', 'SarBay Volleyball Tournament', 'Description: A beach volleyball competition held during the Sarangani Bay Festival, featuring local and national teams.', 'Glan, Sarangani Province', '09:00:00', '2025-05-17', 'Sports', 1, 'approved', 2, '2025-05-02 10:18:02', NULL, NULL),
(19, 'C:/Users/Emnace/Downloads/images (30).jpg', '8th PIFTC 2025', 'Description: Focused on boosting farm tourism, attended by nearly 500 organizations, exhibitors, and officials nationwide.', 'KCC Mall Convention Center, General Santos City', '09:00:00', '2025-02-24', 'Conference', 1, 'approved', 2, '2025-05-02 10:31:24', '2025-05-02 10:45:25', NULL),
(20, 'C:/Users/Emnace/Downloads/486905928_1066298345523745_814514349592722639_n.jpg', '1st IMC Meeting 2025', 'Description: The Department of Agriculture - Regional Field Office XII held its 1st Internal Management Committee Meeting for 2025 to tackle operational challenges and align strategic goals for agricultural development in SOCCSKSARGEN. Led by Regional Executive Director Roberto T. Perales, the event emphasized sustainability, food security, and effective coordination with LGUs and farmers’ groups. The meeting served as a platform for updates on ongoing programs and identifying regional priorities for the fiscal year.', 'Koronadal City, South Cotabato', '12:00:00', '2025-01-06', 'Conference', 1, 'approved', 2, '2025-05-02 10:39:40', NULL, NULL),
(21, 'C:/Users/Emnace/Downloads/492091123_1108674517944900_2073956419176026913_n.jpg', ' Palimbang & Kanipaan CIS', 'Description: The National Irrigation Administration – Sultan Kudarat Irrigation Management Office (NIA-SKIMO) conducted a Pre-Construction Conference to prepare for the implementation of two major irrigation projects: the Palimbang CIS and Kanipaan CIS. Attended by Barangay LGUs and Irrigators’ Associations, the event aimed to align stakeholders on project goals, implementation processes, and timelines. The projects, worth ₱6.8 million and ₱12.2 million respectively, are expected to enhance agricultural productivity in the region. Discussions were focused on procedural compliance, stakeholder responsibilities, and community engagement.', 'Sultan Kudarat, Philippines', '09:00:00', '2025-04-23', 'Conference', 1, 'approved', 2, '2025-05-02 10:43:30', NULL, NULL),
(22, 'C:/Users/Emnace/Downloads/images (31).jpg', 'DepEd XII FolkDance Workshop 2025', 'Description: Workshop on national folk dance and research forum.', 'Region XII', '09:00:00', '2025-04-20', 'Workshop', 1, 'approved', 2, '2025-05-02 11:59:27', NULL, NULL),
(23, 'C:/Users/Emnace/Downloads/494314918_1229428525857424_5928682181521066989_n.jpg', 'Summer Dance Workshop', 'Description: The Summer Dance Workshop Batch 2 offers a fun and engaging way to learn dance for all ages and skill levels. Open to the public, this workshop focuses on foundational and advanced techniques in various dance styles, led by professional instructors. Join and groove your way through the summer!', 'General Santos City', '09:00:00', '2025-05-19', 'Workshop', 1, 'approved', 2, '2025-05-02 12:12:24', NULL, NULL),
(24, 'C:/Users/Emnace/Downloads/487772835_1121324449798020_4807748755154126174_n.jpg', 'Music Summer Workshop', 'Description: A comprehensive summer workshop offering music, arts, and dance lessons to help kids and teens discover and enhance their talents. Includes hands-on learning in instruments like piano, guitar, drums, violin, as well as vocal coaching, painting, and pop/hip-hop dance. Ends with a recital performance.', 'Veranza KCC Activity Center, General Santos City', '09:00:00', '2025-05-11', 'Workshop', 1, 'approved', 2, '2025-05-02 12:17:10', NULL, NULL),
(25, 'C:/Users/Emnace/Downloads/482192668_633528246081509_5427737035764083796_n.jpg', 'Game Dev Workshop', 'Description: The Department of Information and Communications Technology (DICT), through its ICT Industry Development Bureau and the EPIC Program, hosted a dynamic Game Development Workshop in partnership with Kave Guild and SmartHome Davao. With 53 participants, the event covered 2D/3D graphics, animation, environment creation, and simulation. It aimed to empower aspiring game developers across SOCCSKSARGEN.', 'General Santos City, South Cotabato', '09:00:00', '2025-03-10', 'Workshop', 1, 'approved', 2, '2025-05-02 12:20:02', NULL, NULL),
(26, 'C:/Users/Emnace/Downloads/491913220_1051022733744945_4499409455841380409_n.jpg', 'Metrofab Summer Workshop', 'Description: Metrofab launched its 2025 Summer Workshop themed \"Ignite Your Style and Confidence,\" aimed at nurturing aspiring models through confidence-building and fashion-focused training. The workshop drew enthusiastic participants and supportive parents, setting the stage for a transformative summer journey in self-expression and personal growth.', 'General Santos City', '13:00:00', '2025-03-27', 'Workshop', 1, 'pending', 2, '2025-05-02 12:22:45', NULL, NULL),
(27, 'C:/Users/Emnace/Downloads/494233084_122162344244377902_7765802908264814711_n.jpg', 'MW4SP Seminar-Workshop', 'Description: The MW4SP Seminar-Workshop brought together LGU representatives from Cotabato Province and Lake Sebu for an intensive three-day training on crafting improved water, sewerage, and sanitation plans. Participants collaborated through late-night planning sessions and dynamic discussions to ensure that their communities move toward better access to clean water and sanitation services. The event emphasized teamwork, resilience, and a shared vision for healthier communities.', 'Koronadal City, South Cotabato', '09:00:00', '2025-04-28', 'Workshop', 1, 'pending', 2, '2025-05-02 12:29:56', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `feed`
--

CREATE TABLE `feed` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `response` text NOT NULL,
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `places`
--

CREATE TABLE `places` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `image` text DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `date_created` datetime DEFAULT current_timestamp(),
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `places`
--

INSERT INTO `places` (`id`, `user_id`, `image`, `name`, `description`, `category`, `location`, `status`, `date_created`, `date_modified`, `date_deleted`) VALUES
(1, NULL, 'uploads\\places\\20250501213946.jpg', 'Gumasa Beach', 'Operating Hours: Open 24 hours daily\n\nEntrance Fee: Varies by resort; some areas may offer free access\n\nBest Time to Visit: Summer months (March to May), especially during the SarBay Festival\n\nDescription: Known as the \"Small Boracay of Mindanao,\" Gumasa Beach boasts a six-kilometer stretch of powdery white sand and calm turquoise waters. It offers a peaceful escape with beachside resorts, water activities like snorkeling and kayaking, and scenic coastal views. The beach becomes a lively hotspot during the SarBay Festival every May, featuring music, sports, and cultural events.', 'Beach', 'Glan, Sarangani Province, Philippines', 'approved', '2025-05-01 21:39:46', '2025-05-01 23:45:43', NULL),
(2, NULL, 'uploads\\places\\20250501235037.png', 'Tariza Beach Club', 'Operating Hours:\n\nResort Access: Daily, 7:00 AM – 10:00 PM\n\nCheck-in: 2:00 PM\n\nCheck-out: 12:00 PM\n\nDescription:\nTariza Beach Club is a serene beachfront resort nestled along the South Cotabato–Sarangani Road, just 20 minutes from General Santos City. Opened in 2023, this tropical getaway offers air-conditioned rooms with ocean views, private bathrooms, and modern comforts. Guests can unwind in the swimming pool, soak in the hot tub, or relax on the terrace with stunning sea views. The resort is pet-friendly and provides free on-site parking, making it ideal for family vacations, romantic escapes, or peaceful solo retreats.', 'Beach', 'Malapatan, Sarangani Province, Philippines', 'approved', '2025-05-01 21:40:26', '2025-05-01 23:50:37', NULL),
(3, NULL, 'uploads\\places\\20250501214055.png', 'Tuka Marine Park and Beach Resort', 'Operating Hours\n•	Daily: 8:00 AM – 5:00 PM\nNote: Visitors are advised to book their trip at least two days in advance through the Kiamba Tourism Office. \nTuka Marine Park is a protected marine sanctuary comprising four coves, with only Tuka 3 currently open to the public. The park boasts vibrant coral reefs, diverse marine life, and pristine white sand beaches, making it a haven for snorkeling and diving enthusiasts.  \nAccess to the park is regulated to preserve its natural beauty. Visitors must coordinate with the local tourism office for boat transfers and are encouraged to bring their own food and beverages, as there are limited facilities on-site.', 'Beach', 'Kiamba, Sarangani Province, Philippines', 'approved', '2025-05-01 21:40:55', NULL, NULL),
(4, NULL, 'uploads\\places\\20250501214610.png', 'Lake Holon', 'Elevation: Approximately 1,756 meters (5,761 feet)\n\nDescription: Lake Holon, also known as Lake Maughan, is a crater lake nestled within Mount Parker. Recognized for its pristine waters and serene environment, it has been dubbed the \"Crown Jewel of the South.\" The lake is sacred to the T\'boli tribe, and visitors often engage in cultural exchanges during their stay.\n\nActivities: Trekking, camping, cultural immersion\n\nAccess: Treks usually commence from Barangay Salacafe or Barangay Kule. Coordination with the T\'boli Tourism Office is required for permits and guides.\n\nBest Time to Visit: Dry season (November to April) to ensure safer trekking conditions.', 'Mountains', 'T\'boli, South Cotabato, Philippines', 'approved', '2025-05-01 21:46:10', NULL, NULL),
(5, NULL, 'uploads\\places\\20250501214710.jpg', 'La Palmera Mountain Ridges', 'Description: La Palmera Mountain Ridges offer a picturesque landscape of rolling hills adorned with cogon grass, resembling the famed Chocolate Hills of Bohol. This destination gained popularity through social media and has since become a favorite spot for photographers and nature lovers.\n\nActivities: Sightseeing, photography, light trekking\n\nAccess: Visitors typically hire a habal-habal (motorbike) from downtown Columbio for an hour-long ride to the site.\n\nBest Time to Visit: Early morning or late afternoon for optimal lighting and cooler temperatures.', 'Mountains', 'Columbio, Sultan Kudarat, Philippines', 'approved', '2025-05-01 21:47:10', NULL, NULL),
(6, NULL, 'uploads\\places\\20250501215417.png', 'Lake Mofong', 'Description: Lake Mofong is a heart-shaped crater lake nestled atop the mountains of Maasim. The lake holds cultural significance for the indigenous Blaan community and offers a serene environment for visitors. Reaching the lake involves a two-and-a-half-hour trek or a motorcycle ride through rugged trails.\n\nActivities: Hiking, cultural immersion, photography\n\nAccess: Visitors are advised to coordinate with the local tourism office or community guides for assistance and to ensure sustainable tourism practices.\n\nBest Time to Visit: Dry season (November to April) for safer trekking conditions.', 'Mountains', 'Sitio New Canaan, Maasim, Sarangani Province', 'approved', '2025-05-01 21:54:17', NULL, NULL),
(7, NULL, 'uploads\\places\\20250501220748.jpg', 'General Paulino Santos Museum', 'Opening Hours:\n\nMonday to Friday: 8:00 AM – 12:00 PM, 1:00 PM – 5:00 PM\n\nSaturday: 8:00 AM – 12:00 PM\n\nSunday: Closed\n\nThe General Paulino Santos Museum, established in 2003, is the first formal museum in General Santos City. It is dedicated to preserving the legacy of General Paulino Santos, the city\'s namesake and a key figure in its development. The museum houses an extensive collection of his personal belongings, including clothing, diaries, photographs, and documents detailing his work as the administrator of the National Land Settlement Administration (NLSA).', 'Museum', 'General Santos City, South Cotabato, Philippines', 'approved', '2025-05-01 22:07:48', NULL, NULL),
(8, NULL, 'uploads\\places\\20250501222841.jpg', 'Sarangani Provincial Museum ', 'Located within the Capitol Complex, this museum features exhibits on Sarangani Bay\'s marine life and the province\'s cultural heritage. It\'s a central venue for the annual MunaTo Festival, celebrating Sarangani\'s founding day.', 'Museum', 'Alabel, Sarangani Province', 'approved', '2025-05-01 22:15:41', '2025-05-01 22:28:41', NULL),
(9, NULL, 'uploads\\places\\20250501222920.jpg', 'Lamlifew Village Museum', 'The Lamlifew Village Museum is a living museum that showcases the rich cultural heritage of the Blaan indigenous people. Visitors can immerse themselves in traditional Blaan life, including their weaving, farming practices, and rituals.', 'Museum', 'Malungon, Sarangani Province', 'approved', '2025-05-01 22:29:20', NULL, NULL),
(10, NULL, 'uploads\\places\\20250501223547.jpeg', 'Kalon Barak Skyline Ridge', 'Description: Perched approximately 750 meters above sea level, Kalon Barak offers panoramic views of Mt. Matutum, Mt. Apo, and Mt. Busa. It\'s a favored spot for witnessing breathtaking sunrises, sunsets, and a mesmerizing sea of clouds.', 'Camping', 'Malungon, Sarangani Province', 'approved', '2025-05-01 22:35:47', NULL, NULL),
(11, NULL, 'uploads\\places\\20250501224119.jpg', 'Lebak Katunggan Eco Park', 'Description: Spanning 720 hectares, this eco-park features a 1.6-kilometer bamboo boardwalk through lush mangrove forests. It\'s a haven for birdwatchers and nature lovers, offering opportunities for beach camping, boating, and educational tours.', 'Camping', 'Barangay Taguisa, Lebak, Sultan Kudarat', 'approved', '2025-05-01 22:41:19', NULL, NULL),
(12, NULL, 'uploads\\places\\20250501224302.jpg', 'Esperanza Hot and Cold Springs', 'Description: Nestled within the Allah Valley, these natural springs offer a serene environment for camping. The area provides both hot and cold springs, surrounded by lush greenery, making it ideal for relaxation and nature appreciation.', 'Camping', 'Esperanza, Sultan Kudarat', 'approved', '2025-05-01 22:43:02', '2025-05-02 01:02:50', NULL),
(13, NULL, 'uploads\\places\\20250501230251.jpg', 'Sanchez Peak', 'Description: Sanchez Peak has become a go-to hiking spot for both locals and tourists due to its accessibility and stunning views. Rising approximately 800 feet above sea level, the peak provides a full view of GenSan’s cityscape, Mt. Matutum, and Sarangani Bay. Trails are well-maintained and perfect for beginners or day hikers looking for a scenic escape from the city.', 'Hiking', 'Olympog, General Santos City', 'approved', '2025-05-01 23:02:51', NULL, NULL),
(14, NULL, 'uploads\\places\\20250501230636.jpg', 'Buko-Buko Peak ', 'Description: Nicknamed the \"New Zealand of the South,\" Buko-Buko Peak enchants visitors with its rolling grasslands, open blue skies, and breezy highland air. A short trek from the city, this trail is ideal for those seeking calm and picturesque surroundings. The ridge-like formation of the hill offers panoramic photo opportunities that attract content creators and drone enthusiasts alike.', 'Hiking', 'Olympog, General Santos City', 'approved', '2025-05-01 23:06:36', NULL, NULL),
(15, NULL, 'uploads\\places\\20250501230946.jpg', 'Akir-Akir Mountain', 'Description: Akir-Akir Mountain remains one of the hidden gems of SOCCSKSARGEN, offering solitude and untouched landscapes. This off-the-beaten-path destination is perfect for hikers seeking serenity and immersion in raw nature. The trail leads through thick foliage, gentle inclines, and overlooks that reward you with unspoiled views of the surrounding valley. Due to its relative obscurity, it offers a unique chance to appreciate the wilderness without the usual crowds.', 'Hiking', 'Cotabato Province', 'approved', '2025-05-01 23:09:46', NULL, NULL),
(16, 2, 'C:/Users/Emnace/Downloads/SG+Farm+-+Tupi.jpg', 'SG Farm', 'Description: SG Farm is a popular farm tourism destination in South Cotabato, known for its organic farming practices and sustainable agriculture. The farm offers various activities such as fruit picking, organic vegetable harvesting, and farm tours. Visitors can also enjoy fresh farm-to-table meals prepared from locally grown produce.', 'Farm', 'Polomolok, South Cotabato', 'approved', '2025-05-01 23:17:04', NULL, NULL),
(17, 2, 'C:/Users/Emnace/Downloads/images (20).jpg', 'Eden’s Flower Farm', 'Operating Hours:\n\nDays Open: Monday to Saturday\n\nTime: 7:00 AM to 4:00 PM\n\nDescription: Eden’s Flower Farm is a picturesque flower garden nestled in the cool highlands of Tupi, South Cotabato. Established in 2014, it has become a popular destination for both locals and tourists. The farm is renowned for its vibrant fields of chrysanthemums, which bloom in a stunning array of colors, creating a \"sea of flowers\" that attracts visitors seeking both natural beauty and a tranquil escape. Description: Eden’s Flower Farm is a picturesque flower garden nestled in the cool highlands of Tupi, South Cotabato. Established in 2014, it has become a popular destination for both locals and tourists. The farm is renowned for its vibrant fields of chrysanthemums, which bloom in a stunning array of colors, creating a \"sea of flowers\" that attracts visitors seeking both natural beauty and a tranquil escape.', 'Farm', 'Tupi, South Cotabato', 'approved', '2025-05-01 23:28:50', NULL, NULL),
(18, 2, 'C:/Users/Emnace/Downloads/download (12).jpg', 'Kolondatal Farm', 'Description: Kolondatal Farm is quickly gaining recognition as one of South Cotabato\'s top agritourism spots. Known for its expansive pineapple plantations, this farm also grows a variety of high-value crops like bananas, corn, and vegetables. Visitors can explore the farm through guided tours, gaining insight into modern farming techniques and sustainable agricultural practices that are vital to the region\'s economy. The serene surroundings, coupled with the farm\'s educational offerings, make it an ideal destination for nature lovers, students, and families seeking to learn more about farming and agriculture.', 'Farm', 'Tampakan, South Cotabato', 'approved', '2025-05-01 23:41:07', NULL, NULL),
(19, 2, 'C:/Users/Emnace/Downloads/Lake-Sebu.jpg', ' Seven Falls', 'Description: Seven Falls is a majestic cluster of seven waterfalls located in the highlands of Lake Sebu. The most accessible among them is Hikong Alo, while the others—especially Hikong Bente, Hikong B’Lebel, and Hikong Tonok—require trekking through forested terrain. Each cascade is uniquely stunning, nestled in the misty mountains and surrounded by dense foliage. Visitors can experience the exhilarating zipline ride—the highest in Southeast Asia—that offers aerial views of the waterfalls and forest canopy. Cultural encounters with the indigenous T\'boli people also enrich the visit, with opportunities to see their traditional weaving and music.', 'Waterfalls', 'Lake Sebu, South Cotabato', 'approved', '2025-05-02 00:13:42', NULL, NULL),
(20, 2, 'C:/Users/Emnace/Downloads/Asik-Asik-Falls.jpg', 'Asik-Asik Falls', 'Description: Asik-Asik Falls is a one-of-a-kind natural wonder featuring a curtain of spring water gushing from a lush, vegetated cliff—there’s no visible river above, making the phenomenon even more intriguing. Discovered by the public only in the early 2010s, it has quickly risen to fame as one of the most photogenic waterfalls in Mindanao. Visitors trek down a stone stairway to reach the falls, where they can wade into the shallow waters or take a refreshing dip. Surrounded by the verdant highlands of Alamada, it’s perfect for nature lovers, photographers, and adventure seekers.', 'Waterfalls', 'Alamada, Cotabato', 'approved', '2025-05-02 00:15:21', NULL, NULL),
(21, 2, 'C:/Users/Emnace/Downloads/download (13).jpg', 'Matigol Falls', 'Description: Tucked deep within the mountains of Arakan, Matigol Falls is a multi-level cascade surrounded by mossy rocks and lush rainforest. The trail to the falls involves a moderately challenging trek, passing by rivers and scenic viewpoints. It’s a great destination for eco-tourists and hikers looking to escape the usual crowd. The cool waters and raw beauty of the falls offer a truly immersive nature experience. Nearby, visitors can also explore caves and other minor waterfalls that make Arakan a rising eco-adventure spot.', 'Waterfalls', 'Arakan, Cotabato', 'approved', '2025-05-02 00:17:33', NULL, NULL),
(22, 2, 'C:/Users/Emnace/Downloads/images (21).jpg', 'Brigada Golf Range', 'Description: The Brigada Golf Range is a state-of-the-art facility that offers a refreshing and inviting environment for golfers of all levels. Nestled in the lively center of General Santos City, it provides a chill hangout spot and a fun sport for all ages, making it perfect for midweek bonding.', 'Golf', 'General Santos City, South Cotabato', 'approved', '2025-05-02 00:25:55', '2025-05-02 00:37:46', NULL),
(23, 2, 'C:/Users/Emnace/Downloads/sarangani-golf-country-club.jpg', 'Sarangani Golf & Country Club ', 'Description: A 9-hole golf course situated on rolling terrain with mango and hardwood trees. The course features miniature lakes and offers a relaxing environment for golfers.', 'Golf', 'Malungon, Sarangani Province', 'approved', '2025-05-02 00:33:02', NULL, NULL),
(24, 2, 'C:/Users/Emnace/Downloads/images (22).jpg', 'Brittannika Golf Course', 'Description: A newly developed golf course featuring a mix of par-3 and par-4 holes. It\'s designed to cater to both beginners and experienced golfers. The course is set in a scenic location, offering a peaceful golfing experience.', 'Golf', 'Tupi, South Cotabato', 'approved', '2025-05-02 00:34:41', '2025-05-04 12:05:39', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `place_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL CHECK (`rating` between 1 and 5),
  `comment` text NOT NULL,
  `date_created` timestamp NOT NULL DEFAULT current_timestamp(),
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `place_id`, `user_id`, `rating`, `comment`, `date_created`, `date_modified`, `date_deleted`) VALUES
(1, 2, 2, 5, 'nice', '2025-05-01 16:44:08', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `review_replies`
--

CREATE TABLE `review_replies` (
  `id` int(11) NOT NULL,
  `review_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `reply_text` text NOT NULL,
  `date_created` timestamp NOT NULL DEFAULT current_timestamp(),
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `saved_places`
--

CREATE TABLE `saved_places` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `place_id` int(11) NOT NULL,
  `date_saved` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `saved_places`
--

INSERT INTO `saved_places` (`id`, `user_id`, `place_id`, `date_saved`) VALUES
(4, 2, 2, '2025-05-04 08:51:03'),
(5, 2, 1, '2025-05-04 10:10:13');

-- --------------------------------------------------------

--
-- Table structure for table `user_accounts`
--

CREATE TABLE `user_accounts` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `profile_picture_path` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','user') NOT NULL,
  `status` enum('active','inactive') DEFAULT 'active',
  `date_created` timestamp NOT NULL DEFAULT current_timestamp(),
  `date_modified` datetime DEFAULT NULL,
  `date_deleted` datetime DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL,
  `is_online` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_accounts`
--

INSERT INTO `user_accounts` (`id`, `username`, `address`, `email`, `profile_picture_path`, `phone`, `password_hash`, `role`, `status`, `date_created`, `date_modified`, `date_deleted`, `last_activity`, `is_online`) VALUES
(1, 'admin', 'fatima uhaw general santos city', 'jazferjohnemnace@gmail.com', 'profile_pictures\\user_1_1746119848.png', '09556795202', '$2b$12$0PJOXwyvsqoO55JXXHXWfuoLd/rhAeGKzTAob2DmvALffwo6kT.NK', 'admin', 'active', '2025-05-01 11:41:24', NULL, NULL, '2025-05-04 12:04:04', 1),
(2, 'jaz4yo', 'fatima uhaw general santos city', 'bboyemnace@gmail.com', 'profile_pictures\\user_2_1746117927.png', '09556795202', '$2b$12$NQcMSS3TzZPw7Ysl5/L6geq5bxmsuzMdERNGvwWCf6qVFJn.x/2xG', 'user', 'active', '2025-05-01 11:44:25', NULL, NULL, '2025-05-04 19:00:33', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `feed`
--
ALTER TABLE `feed`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `places`
--
ALTER TABLE `places`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `place_id` (`place_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `review_replies`
--
ALTER TABLE `review_replies`
  ADD PRIMARY KEY (`id`),
  ADD KEY `review_id` (`review_id`),
  ADD KEY `admin_id` (`admin_id`);

--
-- Indexes for table `saved_places`
--
ALTER TABLE `saved_places`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_saved_place` (`user_id`,`place_id`),
  ADD KEY `place_id` (`place_id`);

--
-- Indexes for table `user_accounts`
--
ALTER TABLE `user_accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `feed`
--
ALTER TABLE `feed`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `places`
--
ALTER TABLE `places`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `review_replies`
--
ALTER TABLE `review_replies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `saved_places`
--
ALTER TABLE `saved_places`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user_accounts`
--
ALTER TABLE `user_accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `events`
--
ALTER TABLE `events`
  ADD CONSTRAINT `events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`id`);

--
-- Constraints for table `feed`
--
ALTER TABLE `feed`
  ADD CONSTRAINT `feed_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `places`
--
ALTER TABLE `places`
  ADD CONSTRAINT `places_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`place_id`) REFERENCES `places` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `review_replies`
--
ALTER TABLE `review_replies`
  ADD CONSTRAINT `review_replies_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `reviews` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `review_replies_ibfk_2` FOREIGN KEY (`admin_id`) REFERENCES `user_accounts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `saved_places`
--
ALTER TABLE `saved_places`
  ADD CONSTRAINT `saved_places_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saved_places_ibfk_2` FOREIGN KEY (`place_id`) REFERENCES `places` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
