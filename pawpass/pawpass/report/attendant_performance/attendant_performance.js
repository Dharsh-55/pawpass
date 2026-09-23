// Copyright (c) 2026, Dharshini  and contributors
// For license information, please see license.txt

frappe.query_reports["Attendant Performance"] = {
	filters: [
		{
			fieldname: "from_date", label: "From Date",
			fieldtype: "Date", reqd: 1
		},
		{
			fieldname: "to_date", label: "To Date",
			fieldtype: "Date", reqd: 1
		},
		{
			fieldname: "attendant", label: "Attendant",
			fieldtype: "Link", options: "Attendant"
		}
	],

	formatter: function(value, row, column, data){
		if (column.fieldname=="completion_rate"){
			if (data.completion_rate<70)
				return `<span style="color:red">${value}</span>`;
			if (data.completion_rate>=90)
				return `<span style="color:green">${value}</span>`;
		}
		return value;
	}
};
