<h3 id="updateTime">Update Time: </h3>

<div class="first_row">
            <div class="navigation">
		<a href="index.html"><button>Overview</button></a>
		<a href="assets.html"><button>Assets</button></a>
		<a href="positions.html"><button>Positions</button></a>
		<a href="breakdown.html"><button>Breakdown</button></a>
		<a href="leverage.html"><button>Leverage</button></a>
		<a href="funding.html"><button>Funding</button></a>
		<a href="currentFunding.html"><button>Current Funding</button></a>
		<a href="report.html"><button>Report</button></a>
		<a href="test_page.php"><button>Rewards Cumulative</button></a>
		<a href="spread.html"><button>Spread</button></a>
                <a href="loans.php"><button>Loans</button></a>
		<a href="nav.html"><button>GAV</button></a>
		<a href="daily_cum.php"><button>24 Hour Report</button></a>
		<a href="monthly_reward.php"><button>Monthly Report</button></a>
		<a href="daily_calculation.php"><button>Daily Calculation</button></a>
		<a href="http://52.56.101.27/hist.html"><button>Historic Funding</button></a>
	</div>
</div>
<br><br>

<form method="post">
	<label for="gen">Generate Table</label>
	<button type="submit">Execute</button>
</form>

<?php
echo "<!DOCTYPE html>";
echo "<html lang='en'>";
echo "<head>";
echo "<meta charset='UTF-8'>";
echo "<title>MNSF Dashboard</title>";

// Add inline CSS within a <style> tag
echo "<style>";
echo "html {";
echo "  background-color: rgb(22, 37, 49);"; // Background color for <html>
echo "  font-family: 'Segoe UI';";
echo "  display: flex;";
echo "  justify-content: center;";
echo "  height: 100%;"; // Ensure <html> takes full height
echo "}";
echo "body {";
echo "  margin: 0;"; // Remove default margin from body
echo "  width: 100%;"; // Ensure body takes full width
echo "  height: 100%;"; // Ensure body takes full height
echo "}";
echo ".fillBack {";
echo "  background-color: rgb(34, 48, 60);";
echo "}";
echo "table, th, td {";
echo "  border: 1px solid;";
echo "  border-collapse: collapse;";
echo "  background-color: rgb(34, 48, 60);";
echo "  color: rgb(234, 255, 253);";
echo "  font-size: 16px;";
echo "}";
echo "th {";
echo "  color: rgb(255, 255, 255);";
echo "}";
echo "th, td {";
echo "  padding: 1px;";
echo "}";
echo "a {";
echo "	color: rgb(255, 255, 255);";
echo "}";
echo "label {";
echo " color: rgb(255, 255, 255);";
echo "	padding-left: 15px;";
echo "}";
echo "h3 {";
echo "  color: rgb(255, 255, 255);";
echo "}";
echo "h2 {";
echo "  color: rgb(255, 255, 255);";
echo "  font-size: 22px;";
echo "  background-color: rgb(34, 48, 60);";
echo "  justify-content: center;";
echo "  border-bottom: 1px rgba(255, 255, 255, 0.5) solid;";
echo "}";
echo ".first_row {";
echo "  width: auto;";
echo "  height: auto;";
echo "  justify-content: center;";
echo "  background-color: rgb(34, 48, 60);";
echo "  text-align: center;";
echo "}";
echo "button {";
echo "  cursor: grab;";
echo "}";
echo ".second_row,";
echo ".third_row,";
echo ".fourth_row {";
echo "  width: auto;";
echo "  height: auto;";
echo "  background-color: rgb(34, 48, 60);";
echo "  justify-content: center;";
echo "  display: flex;";
echo "  padding: 5px;";
echo "  padding-bottom: 20px;";
echo "}";
echo ".balances,";
echo ".coinAsset,";
echo ".USDAsset {";
echo "  display: inline-table;";
echo "  padding-left: 10px;";
echo "  padding-right: 10px;";
echo "}";
echo "</style>";

echo "</head>";
echo "<body>";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
	$gav_query = "python3 /home/ubuntu/tran_test/main/monthly_gav.py";

        //echo $gav_query;

        $gav_output_month = '/tmp/gav_output_month.txt';
        shell_exec("$gav_query > $gav_output_month 2>&1");
        $o_output = file_get_contents($gav_output_month);

        echo "<div class='fourth_row'>";
        echo "<div class='fillBack'>";

        $numeric_output = floatval($o_output);

        echo "<h2>Month to Date Gav Difference</h2>";
        echo "<h3>" . number_format($numeric_output, 2) . "</h3>";
        //var_dump($o_output);

        echo "</div>";
        echo "</div>";

	$date = new DateTime("now", new DateTimeZone("Europe/London"));
	$epoch_timeski = $date->getTimeStamp();

	$isBST = $date->format('I');

	if ($isBST) {
		$offset = 82800;
	} else {
		$offset = 86400;
	}

	$currentEpoch = time();

	$oldEpoch = $currentEpoch - $offset; //860400; 82800; //sets time 23 hours back to adjust for timezone

	$queryTime = date("H-i", $oldEpoch);
	$queryDate_old = date("Y-m-d", $oldEpoch);
	$queryDate = date("Y-m-d");

	//$query = "python3 /home/ubuntu/tran_test/main/second_main.py 14-37 2024-10-08 2024-10-09";


	$query = "python3 /home/ubuntu/tran_test/main/monthly_main.py";

	//echo "sudo " . $query;

	$output_file = '/tmp/output_month.txt';
	shell_exec("$query > $output_file 2>&1");
	$output = file_get_contents($output_file);

	//echo $output;

	$lines = explode("\n", trim($output));

	$headers = explode(",", trim($lines[0]));

	array_splice($lines, 0, 1);

    	//array_pop($lines);


	echo "<div class='fourth_row'>";
   	echo "<div class='fillBack'>";

    	echo "<table>";

	echo "<h2>Month Start Rewards</h2>";

	echo "<tr>";
	foreach ($headers as $header) {
       		echo "<th>" . $header . "</th>";
   	}
    	echo "</tr>";

    	//echo "<tr>";
    	//echo "<td>" . "Test cell" . "</td>";
    	foreach ($lines as $line) {
		echo "<tr>";
       		//echo "<td>" . $line . "</td>";
		$cells = explode(",", $line);
		foreach ($cells as $cell) {
    		echo "<td>" . $cell . "</td>";
		}
       		echo "</tr>";
   	}
    	//echo "</tr>";

    	echo "</table>";
    	echo "</div>";
	echo "</div>";

        $q2 = "python3 /home/ubuntu/tran_test/main/monthly_fund.py";


        //echo "sudo " . $q2;

        //echo "<h2>24Hour Funding Fee</h2>";

        $output_file = '/tmp/output_6.txt';
        shell_exec("$q2 > $output_file 2>&1");
        $output = file_get_contents($output_file);

        $lines = explode("\n", trim($output));

        $headers = explode(",", trim($lines[0]));

        array_splice($lines, 0, 1);

        //array_pop($lines);


        echo "<div class='fourth_row'>";
        echo "<div class='fillBack'>";

        echo "<h2>Month Start Funding Fee</h2>";

        echo "<table>";

        echo "<tr>";
        foreach ($headers as $header) {
                echo "<th>" . $header . "</th>";
        }
        echo "</tr>";

        //echo "<tr>";
        //echo "<td>" . "Test cell" . "</td>";
        foreach ($lines as $line) {
                echo "<tr>";
                //echo "<td>" . $line . "</td>";
                $cells = explode(",", $line);
                foreach ($cells as $cell) {
                echo "<td>" . $cell . "</td>";
                }
                echo "</tr>";
        }
        //echo "</tr>";

        echo "</table>";
        echo "</div>";
        echo "</div>";

}
?>
