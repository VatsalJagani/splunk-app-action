require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/simplexml/ready!'
], function(_, $, mvc, TableView) {
     // Row Coloring Example with custom, client-side range interpretation
    var CustomRangeRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            // Enable this custom cell renderer for both the active_hist_searches and the active_realtime_searches field
            return _(['answered', 'Answered']).contains(cell.field);
        },
        render: function($td, cell) {
            // Add a class to the cell based on the returned value
            var value = parseFloat(cell.value);
            // Apply interpretation for number of historical searches
            if (cell.field === 'answered') {
                if (value > 0) {
			$td.addClass('range-cell').addClass('answered');
			$td.text("Yes");
                } else {
			$td.addClass('range-cell').addClass('unanswered');
			$td.text("No");
		}
            }
            // Apply interpretation for number of realtime searches
            if (cell.field === 'Answered') {
                if (value > 0) {
			$td.addClass('range-cell').addClass('answered');
			$td.text("Yes");
                } else {
			$td.addClass('range-cell').addClass('unanswered');
			$td.text("No");
		}
            }
            // Update the cell content
            //$td.text(value.toFixed(2));
        }
    });
    mvc.Components.get('highlight').getVisualization(function(tableView) {
        tableView.on('rendered', function() {
            // Apply class of the cells to the parent row in order to color the whole row
            tableView.$el.find('td.range-cell').each(function() {
                $(this).parents('tr').addClass(this.className);
            });
        });
        // Add custom cell renderer, the table will re-render automatically.
        tableView.addCellRenderer(new CustomRangeRenderer());
    });
});