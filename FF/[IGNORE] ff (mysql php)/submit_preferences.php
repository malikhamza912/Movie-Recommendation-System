<?php
header('Content-Type: application/json');

$host = 'localhost';
$db = 'movie_recommendation';
$user = 'root'; // Replace with your database username
$password = ''; // Replace with your database password

try {
    $conn = new PDO("mysql:host=$host;dbname=$db", $user, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch user preferences from the request
    $data = json_decode(file_get_contents('php://input'), true);
    $userId = $data['userId'];

    // Step 1: Fetch all user ratings to build a user-movie matrix
    $stmt = $conn->query("SELECT userId, movieId, rating FROM ratings");
    $ratings = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Step 2: Organize ratings into a user-movie matrix
    $userMovieMatrix = [];
    foreach ($ratings as $rating) {
        $userMovieMatrix[$rating['userId']][$rating['movieId']] = $rating['rating'];
    }

    // Step 3: Calculate similarities between the target user and all other users
    function calculateSimilarity($userRatings, $otherRatings) {
        $commonMovies = array_intersect_key($userRatings, $otherRatings);

        if (count($commonMovies) === 0) return 0; // No common movies

        $userValues = [];
        $otherValues = [];

        foreach ($commonMovies as $movieId => $_) {
            $userValues[] = $userRatings[$movieId];
            $otherValues[] = $otherRatings[$movieId];
        }

        // Calculate Pearson correlation
        $meanUser = array_sum($userValues) / count($userValues);
        $meanOther = array_sum($otherValues) / count($otherValues);

        $numerator = 0;
        $denominatorUser = 0;
        $denominatorOther = 0;

        for ($i = 0; $i < count($userValues); $i++) {
            $diffUser = $userValues[$i] - $meanUser;
            $diffOther = $otherValues[$i] - $meanOther;

            $numerator += $diffUser * $diffOther;
            $denominatorUser += $diffUser ** 2;
            $denominatorOther += $diffOther ** 2;
        }

        if ($denominatorUser === 0 || $denominatorOther === 0) return 0;

        return $numerator / sqrt($denominatorUser * $denominatorOther);
    }

    $similarities = [];
    $targetUserRatings = $userMovieMatrix[$userId] ?? [];

    foreach ($userMovieMatrix as $otherUserId => $otherRatings) {
        if ($otherUserId != $userId) {
            $similarities[$otherUserId] = calculateSimilarity($targetUserRatings, $otherRatings);
        }
    }

    // Step 4: Predict movie ratings for the target user
    $movieScores = [];
    $similaritySums = [];

    foreach ($similarities as $otherUserId => $similarity) {
        if ($similarity > 0) {
            foreach ($userMovieMatrix[$otherUserId] as $movieId => $rating) {
                if (!isset($targetUserRatings[$movieId])) {
                    // Weighted score calculation
                    $movieScores[$movieId] = ($movieScores[$movieId] ?? 0) + $similarity * $rating;
                    $similaritySums[$movieId] = ($similaritySums[$movieId] ?? 0) + $similarity;
                }
            }
        }
    }

    // Normalize scores by similarity sums
    $predictedRatings = [];
    foreach ($movieScores as $movieId => $score) {
        $predictedRatings[$movieId] = $score / $similaritySums[$movieId];
    }

    // Step 5: Recommend top 10 movies
    arsort($predictedRatings);
    $topMovieIds = array_slice(array_keys($predictedRatings), 0, 10);

    // Fetch movie titles for the recommendations
    $placeholders = implode(',', array_fill(0, count($topMovieIds), '?'));
    $stmt = $conn->prepare("SELECT title FROM movies WHERE movieId IN ($placeholders)");
    $stmt->execute($topMovieIds);
    $recommendedMovies = $stmt->fetchAll(PDO::FETCH_COLUMN);

    echo json_encode(['recommendations' => $recommendedMovies]);
} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
