<?php
header('Content-Type: application/json');

$host = 'localhost';
$db = 'movie_recommendation';
$user = 'root'; // Replace with your database username
$password = ''; // Replace with your database password

try {
    $conn = new PDO("mysql:host=$host;dbname=$db", $user, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $stmt = $conn->query("SELECT DISTINCT userId FROM ratings");
    $userIds = $stmt->fetchAll(PDO::FETCH_COLUMN);

    echo json_encode(['userIds' => $userIds]);
} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>
