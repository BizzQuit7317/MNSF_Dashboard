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

<?php
echo '<meta http-equiv="refresh" content="300">'; //300:5 mins 
echo "<style>";
//echo ".data-output {";
//echo "	width: 100%;";
//echo "	overflow-x: auto;";
//echo "	white-space: pre-wrap;";
//echo "}";
echo "h1 {";
echo "	color: rgb(255, 255, 255)";
echo "}";
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
echo "table {";
echo "  margin: 0 auto;"; /* Center the table */
echo "  border-collapse: collapse;"; /* Ensure borders are collapsed for grid lines */
echo "  background-color: rgb(34, 48, 60);";
echo "  color: rgb(234, 255, 253);";
echo "  font-size: 16px;";
echo "  width: auto;"; /* Set the width to auto to allow centering */
echo "}";
echo "th, td {";
echo "  border: 1px solid rgb(255, 255, 255);"; /* Add border to th and td for grid lines */
echo "  padding: 1px;";
echo "  text-align: left;"; /* Center text in header and data cells */
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
echo "	justify-content: center;";
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
echo "pre {";
echo "	color: rgb(255, 255, 255);";
echo "  display: flex;";
echo "  justify-content: center;";
echo "}";
echo "</style>";

// Path to your Python script
$pythonScript = "/var/www/html/fireBlocksFunctions_updated.py";

// Execute the Python script and capture the output
$output = shell_exec("python3 " . escapeshellarg($pythonScript));

// Seperating the datasets
$lines = explode("\n\n", trim($output));
$top_table = $lines[0];
$break_down_table = $lines[2];

// Display the output
echo "<div class=fillBack>";
echo "<div class='data_output'><pre>$output</pre></div>";
echo "</div>";
?>
