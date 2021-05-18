// -*- coding:utf-8 mode:javascript -*-
// File: oia_handler.js
// Copyright (C) 2021 by m.na.akei 
// Time-stamp: <2021-05-15 17:45:07>

/* exported */

function oia_dblclick_from_td(val_dic){
    console.log(val_dic, KEY_SHIFT);
    let html_url="csv_print_html_sample.html";
    let nrec= val_dic["nrec"]; // record number in csv
    let id_in_html="rid_"+nrec;
    let url=html_url+"#"+id_in_html;
    window.open(url,"__blank");
}

//-------------
// Local Variables:
// mode: javascript
// coding: utf-8-unix
// End:

