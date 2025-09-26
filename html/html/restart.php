<head>
<title>MNSF Restart Page</title>
</head>

<div>
<a href="index.html"><button>Return</button></a>
<br><br>
</div>

<div class="first_row">
<form method="post">
	<button type="submit" id="stop_button" name="stop_button">Stop Service</button>
	<button type="submit" id="start_button" name="start_button">Start Service</button>
	<button type="submit" id="manual_run" name="manual_run">Run Monitor.py</button>
</form>
<br><br>
</div>
<?php
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
//print_r(getenv());
//echo "<br><br>";

//$script_path = '/var/www/html/utils/service.sh';
//$command = "/bin/bash $script_path stop";
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['stop_button'])) {
	$command = "sudo /bin/bash /var/www/html/utils/service.sh";
	$action = "stop";

	$output = [];
	$return_var = 0;
	//exec($command . "2>&1", $output, $return_var);
	exec("$command $action 2>&1", $output, $return_var);

	//echo "Command: $command<br>";
	echo "<div class='fillBack'>";
	echo "<div class='second_row'>";
	echo "Output:<br>" . nl2br(implode("\n", $output)) . "<br>";
	echo "</div>";
	echo "</div>";
	//echo "Return Code: $return_var<br>";
}
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['start_button'])) {
        $command = "sudo /bin/bash /var/www/html/utils/service.sh";
        $action = "start";

        $output = [];
        $return_var = 0;
        //exec($command . "2>&1", $output, $return_var);
        exec("$command $action 2>&1", $output, $return_var);

	//echo "Command: $command<br>";
	echo "<div class='fillBack'>";
	echo "<div class='second_row'>";
	echo "    Output:<br>" . nl2br(implode("\n", $output)) . "<br>";
	echo "</div>";
	echo "</div>";
        //echo "Return Code: $return_var<br>";
}
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['manual_run'])) {
	$command = "sudo /bin/bash /var/www/html/utils/service.sh";
        $action = "stop";

        $output = [];
        $return_var = 0;
        //exec($command . "2>&1", $output, $return_var);
        exec("$command $action 2>&1", $output, $return_var);

	//echo "Command: $command<br>";

	echo "<div class='fillBack'>";
	echo "<div class='second_row'>";
        echo "    Output:<br>" . nl2br(implode("\n", $output)) . "<br>";
	echo "</div>";
	echo "</div>";

	$command = "sudo python3 /var/www/html/monitor.py";

	$output = [];
	$return_var = 0;

	chdir("/var/www/html/");
	exec("$command $action 2>&1", $output, $return_var);
	
	echo "<div class='fillBack'>";
	echo "<div class='second_row'>";
	echo "    Output:<br>" . nl2br(implode("\n", $output)) . "<br>";
	echo "</div>";
	echo "</div>";
}
?>
