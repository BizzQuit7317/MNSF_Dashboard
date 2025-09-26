<?php

if(isset($_GET['search_query'])) {
        $search_query = $_GET['search_query'];
        $format_query = strtoupper($search_query);
        $format_query_final = "'" . $format_query . "'";

        //echo "You searched for: " . $format_query_final . "\n||||||||\n";
        //echo "\n";
} else {
        echo "No search query entered.";
}

$file_path = "/var/www/html/html/html/tmp.py";

$current_data = file_exists($file_path) ? file_get_contents($file_path) : '';

$current_data = explode('rewards', $current_data);
$current_data = explode('report', $current_data[1]);
$current_data = "rewards" . $current_data[0];

//print_r($current_data);

$init_array = explode('}', $current_data);
$counter = 0;
$new_array = array();

foreach ($init_array as $value) {
        $value_array = explode(',', $value);
        if ($counter != 0){
                $symbol = explode(':', $value_array[3]);
                $trimmed_format_query_final = trim($format_query_final);
                $trimmed_symbol = trim($symbol[1]);

                if ($trimmed_symbol == $trimmed_format_query_final) {
                        $line_string = implode(',', $value_array);
                        $new_array[] = $line_string;
                }
        } else {
                $symbol = explode(':', $value_array[2]);
                $trimmed_format_query_final = trim($format_query_final);
                $trimmed_symbol = trim($symbol[1]);

                if ($trimmed_symbol == $trimmed_format_query_final) {
                        $line_string = implode(',', $value_array);
                        $new_array[] = $line_string;
                }
        }
        $counter++;
}

$new_string = implode('}', $new_array);
$new_string = $new_string . "}]";
if ($new_string[0] == ',') {
        $new_string = "rewards = [" . substr($new_string, 1);
}
echo $new_string;

$file_path_write = "rewards_values.py";
$file = fopen($file_path_write, "w");

if ($file) {
        fwrite($file, $new_string);

        fclose($file);

        echo "\n||||||||\nData has been successfully written to the file.";

        header("Location: http://18.133.174.77/html/html/48h_reward.html");
        exit;
} else {
        echo "Unable to open the file for writing.";
}

?>
