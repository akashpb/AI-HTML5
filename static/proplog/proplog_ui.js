

(function(exports) {

	// ====== module start =========
	
	// configuration for printing to html:

	var result_html_id="result"; // output location in html
	var syntax_html_id="syntax"; // syntax description location in html

	// set by solver as it starts: used for printing to html
		
	var start_time=0; 

	// ====== top level: calling and printing from/to html =====

	/* Top level table solver functions: called from html with a text input.
		Runs the selected solver algorithm, printing the process and result to html.
		
		Takes:
			txt - the propositional problem in DIMACS or formula syntax
			solver_algorithm - "dpll_better"
		Does:
			- calls parsers and converters on the input txt
			- runs the selected prover on the parsed and converted txt
			- injects trace and results to the html page
	*/

	exports.solve = function (txt,solver_algorithm,trace_method) {
		exports.clear_output(); // we need to wait a bit after that
		// avoid doing html dom change in parallel to solving
		window.setTimeout(function(){solve_aux(txt,solver_algorithm,trace_method)},100);
	}  

	function solve_aux(txt,solver_algorithm,trace_method) {
		console.log("solve_aux");
		var parsed,converted,maxvar,clauses,origvars,i,res,txt,stats,res;
		start_time=new Date().getTime();  
		parsed=proplog_parse.parse(txt);
		origvars=[];  
		if (typeof parsed[0]=="number") {
			// dimacs
			clauses=parsed;
			maxvar=clauses.shift();
		} else if (parsed[0]==="error") {
			// err
			show_result("Syntax error: "+parsed[0]);
			return;
		} else {
			// formula
			converted=proplog_convert.formula_to_cnf(parsed); 
			converted=proplog_convert.rename_vars_in_clauses(converted); 
			maxvar=converted[0];
			clauses=converted[1];
			origvars=converted[2];
		}
		// return first el and change clauses by removing the first el: 
		
		res=proplog_dpll.dpll(clauses,maxvar,trace_method,origvars);	
		
		if (res[0]!==false) {                 

			// other methods typically generate a model
			txt="Clause set is <b>true</b> if we assign values to variables as: "; 
			for(i=0;i<res[0].length;i++) txt+=res[0][i]+" "; 
			show_result(txt);
		
		} else {
			// clause set unsatisfiable
			show_result("Clause set is <b>false</b> for all possible assignments to variables.");  
		}   
	}  

	/* Top level truth table and normal form builders.
		
		Takes:
			txt - the propositional problem in DIMACS or formula syntax
			build_select - one of "truth_table","CNF",
		
		Does:
			- calls parsers and converters on the input txt
			- builds the required result
			- injects the result to the html page
	*/


	exports.build = function (txt,build_select) {
		exports.clear_output(); // we need to wait a bit after that
		// avoid doing html dom change in parallel to building
		window.setTimeout(function(){build_aux(txt,build_select)},100);
	}

	function build_aux(txt,build_select) {
		console.log("build_aux");
		var res;
		start_time=new Date().getTime();  
		if (!txt) {
			show_result("No input.");
			return;
		}
		res=proplog_parse.parse(txt);
		console.log(res);
		//show_process("parsing finished");
		if (res[0]==="error") {
			show_result("Parse error: "+res[1]);
			return;
		}
		if (build_select=="parse_tree") {
			if (typeof res[0]==="number") {
				res.shift();
			} 
			res=JSON.stringify(res);
			console.log(res);
			res=res.replace(/"/g,"")
			console.log(res);
			result = res;
			console.log("Test" + result);
			//res=proplog_convert.parsed_print(res,[]);    
		} else if (build_select=="truth_table") {
				res=proplog_convert.print_truthtable(res);
		} else if (build_select=="cnf") {    
			if (typeof res[0]==="number") {
				res.shift();
				res=proplog_convert.parsed_print(res,[]);      
			} else {
				res=proplog_convert.formula_to_cnf(res);
				res=proplog_convert.parsed_print(res,[]);
			}
		}
		show_result("<tt>"+res.replace(/\n/g,"<br>")+"</tt>");  
	}  


	/* clear_output ... are utilities for printing to html

	*/

	exports.clear_output = function() {  
		var place=document.getElementById(result_html_id);
		place.innerHTML=""; 
	}

	function show_result(txt) {
		append_to_place(txt,result_html_id);
	}

	function passed_time() {
		var now=new Date().getTime();  
		var passed=String(now-start_time);
		if ((passed.length)===0) passed="000";
		else if ((passed.length)===1) passed="00"+passed;
		else if ((passed.length)===2) passed="0"+passed;
		return passed;
	}

	function append_to_place(txt,placeid) {
		var place=document.getElementById(placeid);
		var newcontent=document.createElement('div');
		newcontent.innerHTML=txt;
		while (newcontent.firstChild) {
			place.appendChild(newcontent.firstChild);
		} 
	}

	// ====== module end ==========

})(this.proplog_ui = {});
