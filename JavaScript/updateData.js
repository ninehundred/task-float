function updateData(e) {

  var clicked_node = $( this )[ 0 ];
  var clicked_node_column_index = $( this ).index();
  var clicked_node_row_index = $( this ).parent().index();
  var table = $('#tasktable').DataTable(); //our whole table
  var clicked_row_data = table.row( clicked_node_row_index ).data();
  var new_cell_id = String( clicked_node_row_index )  + String( clicked_node_column_index );

  // Make unput with type and ID for proper insertion back into SQL database.
  //TODO: I wonder if this part could be a bit shorter...
  var create_input_node = document.createElement("INPUT");
  create_input_node.setAttribute("id", new_cell_id ); //this is the id of the object we need to focus on!!!
  if ( clicked_node_column_index == 1 || clicked_node_column_index == 2  ) {
    create_input_node.setAttribute("type", "time"); // TODO: change this later for a nicer looking one.
  }
  else if ( clicked_node_column_index == 3 || clicked_node_column_index == 4 ) {
    create_input_node.setAttribute("type", "text");
  }
  else if (clicked_node_column_index == 5 ) {
    create_input_node.setAttribute("type", "number");
    create_input_node.setAttribute("step", "1");
    create_input_node.setAttribute("min", "1");
    create_input_node.setAttribute("max", "3");
  }
  else if (clicked_node_column_index == 6 ) {
      create_input_node.setAttribute("type", "date");
  }
  else if (clicked_node_column_index == 7 ) {
    // row id
    var row_id = String( clicked_row_data[0] );
    // Column Heading (needs to match table heading or have some way of making an equivilent)
    var col_index = String( clicked_node_column_index );
    // update data so task shows as complete
    var output_data = 1;
    $.ajax({
      type: 'POST',
      url: "http://127.0.0.1:5000/tasks",
      data: JSON.stringify({
        "task_post_type" : "task_complete",
        "task_id" : row_id,
        "data" : output_data,
        "col_heading" : col_index,
      }),
      error: function(e) {
        console.log(e);
      },
      dataType: "json",
      contentType: "application/json"
    });
    // remove form control after enter is pushed
    $(".form-control").remove()
    // This reloads the page so that the new data shows up. Ripping fast.
    alert( row_id );
    window.location.reload(false);

  } else {
    return;
  }
  create_input_node.setAttribute("class", "form-control");
  create_input_node.setAttribute("name", "task_input");
  create_input_node.setAttribute("placeholder", "enter task");

  // TODO: maybe we dont replace but just hide so that if the user doesnt enter
  //  anything the cell goes back to normal without us having to implement a
  //  javascript form block...?
  this.replaceChild(create_input_node, this.childNodes[0]);
  $( "#" + new_cell_id ).focus();

  // When user pushes enter the data is sent back to server for reinsertion into the db
  // TODO: a similar function should be made if the user clicks another cell..
  $( '.form-control' ).bind( "enterKey", function (e) {
    var cell_data_input = document.getElementById( new_cell_id );

    // row id
    var row_id = String( clicked_row_data[0] );
    // Data to update the SQL cell with
    var output_data = String( cell_data_input.value );
    // Column Heading (needs to match table heading or have some way of making an equivilent)
    var col_index = String( clicked_node_column_index );

    // tests
    console.log( String( row_id ), String( output_data ), String ( col_index )  );

    $.ajax({
      type: 'POST',
      url: "http://127.0.0.1:5000/tasks",
      data: JSON.stringify({
        "task_post_type" : "task_update",
        "task_id" : row_id,
        "data" : output_data,
        "col_heading" : col_index,
      }),
      error: function(e) {
        console.log(e);
      },
      dataType: "json",
      contentType: "application/json"
    });
    // remove form control after enter is pushed
    $(".form-control").remove()
    //this.replaceChild(create_input_node, this.childNodes[0]);

    // This reloads the page so that the new data shows up. Ripping fast.
    window.location.reload(false);

    //need to say take whatever the user entered and
    });
    $('.form-control').keyup(function(e){
    if(e.keyCode == 13)
    {
      $(this).trigger("enterKey");
    }
  });
});
