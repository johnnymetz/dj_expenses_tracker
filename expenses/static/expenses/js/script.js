app = {};

app.populateSubcategories = function(element, category_to_subcategory){
	category = element.val();
	subcategories = category_to_subcategory[category];
	$('#subcategory').empty();
	$('<option>', {'value': ''}).text('Select one...').appendTo($('#subcategory'));
	$.each(subcategories, function(index, subcategory){
		$('<option>', {'value': subcategory}).text(subcategory).appendTo($('#subcategory'));
	});
};

app.populateMonthlyTotal = function(){
	var monthly_limit = 0;
	$('input.limit').each(function(i, element){
		var value = parseInt($(this).val());
		monthly_limit = monthly_limit + value;
	});
	$('#monthly-limit').text('$' + monthly_limit);
};