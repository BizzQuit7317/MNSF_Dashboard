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
    <label for="sym">Pick a Symbol:</label>
    <!--<input type="text" id="sym" name="sym" value="ATOM">-->
    <select id="sym" name="sym">
        <option value="None">None</option>
        <option value="ATOM">ATOM</option><option value="ATOM.S">ATOM.S</option><option value="AVAX">AVAX</option>
        <option value="CTSI">CTSI</option><option value="DOT.S">DOT.S</option><option value="DOT28.S">DOT28.S</option>
        <option value="ETH">ETH</option><option value="FLOW">FLOW</option><option value="KAVA">KAVA</option>
        <option value="KSM">KSM</option><option value="MINA.S">MINA.S</option><option value="NEAR">NEAR</option>
        <option value="ONE">ONE</option><option value="ROSE">ROSE</option><option value="SCRT">SCRT</option>
        <option value="XETH">XETH</option><option value="XTZ">XTZ</option>
    </select>
    <!--<br><br>-->
    <label for="day">Enter Day:</label>
    <input type="number" id="day" name="day" value=1>
    <!--<br><br>-->
    <label for="exc">Enter Exchange:</label>
    <!--<input type="text" id="exc" name="exc" value="FireBlocks">-->
   <select id="exc" name="exc">
        <option value="None">None</option>
	<option value="FireBlocks">FireBlocks</option><option value="FireBlocks_Cold">FireBlocks_Cold</option><option value="Kraken">Kraken</option><option value="FireBlocks_Bond">FireBlocks_Bond</option>
    </select>
    <br><br>
    <label for="dbi">Enter db_id:</label>
    <!--<input type="text" id="dbi" name="dbi" value="staking">-->
    <select id="dbi" name="dbi">
	<option value="None">None</option><option value="staking">staking</option><option value="staking_2">staking_2</option>
        <option value="staking_3">staking_3</option><option value="staking_4">staking_4</option><option value="staking_5">staking_5</option>
        <option value="cold">cold</option><option value="kraken">kraken</option><option value="available">available</option>
        <option value="un">un</option><option value="bond">bond</option>
    </select>
    <!--<br><br>-->
    <label for="ven">Enter Venue:</label>
    <!--<input type="text" id="ven" name="ven" value="None">-->
    <select id="ven" name="ven">
	<option value="None">None</option><option value="COSMOS">COSMOS</option><option value="KRAKEN">KRAKEN</option>
        <option value="AVAX">AVAX</option><option value="CARTESI">CARTESI</option><option value="ETH">ETH</option>
        <option value="FLOW">FLOW</option><option value="KUSAMA">KUSAMA</option><option value="NEAR">NEAR</option>
        <option value="HARMONY">HARMONY</option><option value="OASIS"></option>OASIS<option value="TEZOS">TEZOS</option>
    </select>
    <!--<br><br>-->
    <label for="_tim">Enter Time:</label>
    <input type="text" id="_tim" name="_tim" value="None">
    <!--<br><br>-->
    <label for="_dat">Enter Date:</label>
    <input type="text" id="_dat" name="_dat" value="None">
    <br><br>
    <button type="submit" style="margin-left: 15px;">Execute</button>
</form>

<script>
    // Get the symbol and exchange elements
    const idSelect = document.getElementById('dbi');
    const excSelect = document.getElementById('exc');
    const symSelect = document.getElementById('sym');
    const dateSelect = document.getElementById('_dat');
    const daySelect = document.getElementById('day');
    const timeSelect = document.getElementById('_tim');

    symSelect.addEventListener('change', function() {
        const selectedSym = symSelect.value;

        if (selectedSym === 'None') {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
                <option value="FireBlocks_Cold">FireBlocks_Cold</option>
                <option value="Kraken">Kraken</option>
                <option value="FireBlocks_Bond">FireBlocks_Bond</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
                <option value="staking_2">staking_2</option>
                <option value="staking_3">staking_3</option>
                <option value="staking_4">staking_4</option>
                <option value="staking_5">staking_5</option>
                <option value="cold">cold</option>
                <option value="kraken">kraken</option>
                <option value="available">available</option>
                <option value="un">un</option>
                <option value="bond">bond</option>
            `;
        } else if (selectedSym === 'ATOM') {
	    excSelect.innerHTML = `
		<option value="None">None</option>		
                <option value="FireBlocks">FireBlocks</option>
                <option value="FireBlocks_Cold">FireBlocks_Cold</option>
                <option value="Kraken">Kraken</option>
            `;
	    idSelect.innerHTML = `
		<option value="None">None</option>		
                <option value="staking">staking</option>
                <option value="cold">cold</option>
                <option value="kraken">kraken</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        } else if (['AVAX', 'NEAR'].includes(selectedSym)) {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        } else if (selectedSym === 'CTSI') {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
                <option value="FireBlocks_Cold">FireBlocks_Cold</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
                <option value="cold">cold</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        } else if (['DOT', 'DOT.S', 'DOT28.S', 'MINA.S', 'XETH', 'XTZ.B'].includes(selectedSym)) {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="Kraken">Kraken</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="kraken">kraken</option>
            `;
            excSelect.value = 'Kraken';
            idSelect.value = 'kraken';
        } else if (selectedSym === 'ETH') {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
                <option value="available">available</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        } else if (['FLOW', 'KAVA', 'ONE', 'ROSE', 'SCRT'].includes(selectedSym)) {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="un">un</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'un';
        } else if (selectedSym === 'KSM') {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
                <option value="FireBlocks_Cold">FireBlocks_Cold</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
                <option value="staking_2">staking_2</option>
                <option value="staking_3">staking_3</option>
                <option value="staking_4">staking_4</option>
                <option value="staking_5">stakin_5</option>
                <option value="cold">cold</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        } else if (selectedSym === 'XTZ') {
            excSelect.innerHTML = `
                <option value="None">None</option>
                <option value="FireBlocks">FireBlocks</option>
                <option value="FireBlocks">FireBlocks_Cold</option>
                <option value="FireBlocks_Bond">FireBlocks_Bond</option>
            `;
            idSelect.innerHTML = `
                <option value="None">None</option>
                <option value="staking">staking</option>
                <option value="cold">cold</option>
                <option value="bond">bond</option>
            `;
            excSelect.value = 'FireBlocks';
            idSelect.value = 'staking';
        }
    });

    dateSelect.addEventListener('change', function() {
        const selectedDate = dateSelect.value;

        if (selectedDate != 'None') {
            daySelect.value = 0;
        }
    });

    timeSelect.addEventListener('change', function() {
        const selectedTime = timeSelect.value;

        if (selectedTime != 'None') {
            daySelect.value = 0;
        }
    });

</script>

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

//$time_file_path = "/var/www/html/html/tmp.py";
//$time_lines = file($time_file_path);

//print_r($time_lines);

//$time_value = null;
//foreach ($lines as $line) {
//	print_r($line);
//	if (strpos(trim($line), 'time') === 0){
//		$time_parts = explode('=', $line);
//		if (isset($time_parts[1])) {
//			$time_value = trim(str_replace('"', '', $time_parts[1]));
//            		break;
//		}
//	}
//}

//if ($time_value) {
//    echo "Extracted time: " . $time_value;
//} else {
//    echo "No 'time' variable found in the Python file.";
//}

//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/index.html\'">Overview</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/assets.html\'">Assets</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/positions.html\'">Positions</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/breakdown.html\'">Breakdown</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/leverage.html\'">Leverage</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/funding.html\'">Funding</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/currentFunding.html\'">Current Funding</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/report.html'">Report</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/test_page.php'">Rewards Cumulative</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/spread.html\'">Spread</button>';
//echo '<button onclick="window.location.href=\'http://18.133.174.77/html/GAV.html\'">GAV</button>';
//echo '<button onclick="window.location.href=\'http://52.56.101.27/hist.html'">Historic Funding</button>';

// Define the allowed command prefix
$allowed_command_prefix = 'python3 /home/ubuntu/tran_test/main/main.py ';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get the command from the POST request
    $sym = isset($_POST['sym']) ? $_POST['sym'] : '';
    $day = isset($_POST['day']) ? $_POST['day'] : '';
    $exc = isset($_POST['exc']) ? $_POST['exc'] : '';
    $dbi = isset($_POST['dbi']) ? $_POST['dbi'] : '';
    $ven = isset($_POST['ven']) ? $_POST['ven'] : '';
    $_tim = isset($_POST['_tim']) ? $_POST['_tim'] : '';
    $_dat = isset($_POST['_dat']) ? $_POST['_dat'] : '';

    $query = $allowed_command_prefix . $sym . ' '  . $day . ' '  . $exc . ' '  . $dbi . ' '  . $ven . ' '  . $_tim . ' '  . $_dat;
    //var_dump($query);
    echo "<br><br>";
    // Redirect output to a file for debugging
    $output_file = '/tmp/output.txt';
    shell_exec("$query > $output_file 2>&1");
    $output = file_get_contents($output_file);
    //echo "<pre>$output</pre>";
   
    $lines = explode("\n", trim($output));

    //$headers = $lines[0];
    $headers = explode(",", trim($lines[0]));

    $cumulative = $lines[count($lines) - 1];

    echo "<a>Cumulative = "  . $cumulative  . "</a>";
    echo "<br>";
    echo "<a> over " . $day  . " days</a>";
    echo "<br>";

    array_splice($lines, 0, 1);

    array_pop($lines);

    //var_dump($headers);

    echo "<div class='fourth_row'>";
    echo "<div class='fillBack'>";

    echo "<table>";

    echo "<tr>";
    //echo "<th>" . "Test header" . "</th>";
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
