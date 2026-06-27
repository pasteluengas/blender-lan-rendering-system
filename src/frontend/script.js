let ip = window.location.hostname;
ip = `http://${ip}:8000`

async function listversions() {
	const res = await fetch(`${ip}/blender-versions`);
	let htmloutput = "";

	const data = await res.json();
	data.version.forEach((v) => {
		console.log(v.version);
		htmloutput = htmloutput + "<option value='" + v.version.replace(".", "-")  +  "'>" + v.version  + "</option>";
	});
	console.log(htmloutput);
	document.getElementById("select-version").innerHTML = htmloutput;
	}

function main() {	
	listversions();

	document.getElementById("input-file").addEventListener("change", (event) => {
		if (event.target.files.length > 0) {
			document.getElementById("input_file_label").style.backgroundColor = "#19853B";
		} else {
			document.getElementById("input_file_label").style.backgroundColor = "#545454";
		}
	});

	function enableLoading() {
		document.getElementById("submit").value = "Loading...";
		document.getElementById("submit").disabled = true;
	}

	function disableLoading() {
		document.getElementById("submit").value = "Send to Render";
		document.getElementById("submit").disabled = false;
	}

	// action="http://192.168.1.17:8000/form/"
	document.getElementById("main_form").addEventListener("submit", async function(e) {
		e.preventDefault();
		const formData = new FormData(this);
		try {
			enableLoading();
			const res = await fetch(`${ip}/form`, {
				method: 'POST',
				body: formData
			});

			if (!res.ok) {
				console.log(error);
				return;
			}

			disableLoading();

			const filesres = await fetch(`${ip}/outputs`);
			const filesdata = await filesres.json();
			let htmloutput = "";
			console.log(filesdata);
			if (filesdata.file.length > 0) {
				console.log(filesdata.file[0].name);
				htmloutput = `<img src='${ip}/outputs/` + filesdata.file[0].name  + "' alt='Blender result'>";
				htmloutput = htmloutput + "<a href='outputs/'>Explore all outputs/ file</a>"
			} else {
				htmloutput = "<p class='red'>Internal Blender Error</p>"
			}

			document.getElementById("div_output").innerHTML = htmloutput;
			
			
		} catch (error) {
			console.log("yeah error: " + error);
		}
	});
}

main();
