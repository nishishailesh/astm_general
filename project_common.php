<?php
//require_once 'Evaluator.php';
require_once('tcpdf/tcpdf.php');

function main_menu()
{
	echo '
		<form method=post class="form-group m-0 p-0">
	
	<div id=main_menu class="dropdown btn-group m-0 p-0">
			<input type=hidden name=session_name value=\''.session_name().'\'>
			<button class="btn btn-outline-primary m-0 p-0" formaction=new_general.php type=submit name=action value=new_general>New</button>
			<button class="btn btn-outline-primary btn-block m-0 p-0" formaction=new_s1.php type=submit name=action value=direct>New Direct</button>
			<button class="btn btn-outline-primary m-0 p-0" formaction=view_database_id.php type=submit name=action value=get_dbid>View Sample ID</button>			
			<button class="btn btn-outline-primary m-0 p-0" formaction=search.php type=submit name=action value=get_search_condition>Search</button>			
			<button class="btn btn-outline-primary m-0 p-0" formaction=view_database_id_from_to_for_print.php type=submit name=action value=get_from_to>Print From-To</button>			
			<button class="btn btn-outline-primary m-0 p-0" formaction=search_and_print.php type=submit name=action value=get_search_condition>Search & Print</button>			
			<button class="btn btn-outline-primary m-0 p-0" formaction=copy_prototype.php type=submit name=action value=copy_prototype>Copy Prototype</button>			
			<button class="btn btn-outline-primary m-0 p-0" formaction=start.php type=submit name=action value=home><img src=img/home.jpeg height=20></button>			
			
			
			<!--<button class="btn btn-outline-primary dropdown-toggle m-0 p-0" type="button" data-toggle="dropdown">New Specific</button>
			<div class="dropdown-menu m-0 p-0">		
					<button class="btn btn-outline-secondary btn-block m-0 p-0" formaction=new_s1.php type=submit name=action value=direct>Direct</button>
					 <button class="btn btn-outline-secondary btn-block m-0 p-0" 
					formaction=new_s2.php type=submit name=action value=new_s2>New S2</button> 
			</div>-->
	</div>
		</form>
	';		
}

function mk_select_from_array($name, $select_array,$disabled='',$default='')
{	
	echo '<select  '.$disabled.' name=\''.$name.'\'>';
	foreach($select_array as $key=>$value)
	{
				//echo $default.'?'.$value;
		if($value==$default)
		{
			echo '<option  selected > '.$value.' </option>';
		}
		else
		{
			echo '<option > '.$value.' </option>';
		}
	}
	echo '</select>';	
	return TRUE;
}


function mk_select_from_array_kv($name, $select_array,$disabled='',$default='')
{	
	echo '<select  '.$disabled.' name=\''.$name.'\'>';
	foreach($select_array as $key=>$value)
	{
				//echo $default.'?'.$value;
		if($value==$default)
		{
			echo '<option  selected value=\''.$key.'\' > '.$value.' </option>';
		}
		else
		{
			echo '<option   value=\''.$key.'\' >'.$value.' </option>';
		}
	}
	echo '</select>';	
	return TRUE;
}


function mk_array_from_sql($link,$sql,$field_name)
{
	$result=run_query($link,$GLOBALS['database'],$sql);
	$ret=array();
	while($ar=get_single_row($result))
	{
		$ret[]=$ar[$field_name];
	}
	return $ret;
}

function mk_array_from_sql_kv($link,$sql,$field_name_k,$field_name_v)
{
	$result=run_query($link,$GLOBALS['database'],$sql);
	$ret=array();
	while($ar=get_single_row($result))
	{
		$ret[$ar[$field_name_k]]=$ar[$field_name_v];
	}
	return $ret;
}

function mk_select_from_sql($link,$sql,$field_name,$select_name,$select_id,$disabled='',$default='')
{
	$ar=mk_array_from_sql($link,$sql,$field_name);
	mk_select_from_array($select_name,$ar,$disabled,$default);
}


function mk_select_from_sql_kv($link,$sql,$field_name_k,$field_name_v,$select_name,$select_id,$disabled='',$default='')
{
	$ar=mk_array_from_sql_kv($link,$sql,$field_name_k,$field_name_v);
	mk_select_from_array_kv($select_name,$ar,$disabled,$default);
}


function get_one_examination_details($link,$examination_id)
{
	$sql='select * from examination where examination_id=\''.$examination_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	
	return $ar=get_single_row($result);
}

function get_protoype_name($link,$prototype_id)
{
	$sql='select * from prototype where prototype_id=\''.$prototype_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	
	return $ar['name'];
}
function view_sample_table($link,$sample_id)
{
	$sql='select * from result where sample_id=\''.$sample_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	
	echo '<table class="table table-striped table-bordered">';
	echo '<tr>
			<td>Encounter ID</td>
			<td colspan=2>';
			sample_id_edit_button($sample_id);
			echo '</td></tr>';
	echo '<tr><th>Examination ID</th><th>Name</th><th>Result</th></tr>';
	while($ar=get_single_row($result))
	{
		//print_r($ar);
		$examination_details=get_one_examination_details($link,$ar['examination_id']);
		//print_r($examination_details);
		echo '	<tr><td>'.$examination_details['examination_id'].'</td>
				<td>'.$examination_details['name'].'</td>
				<td>'.$ar['result'].'</td></tr>';
	}
	
	$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\'';
	$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
	while($ar_blob=get_single_row($result_blob))
	{
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$ar_blob['examination_id']);
		//print_r($examination_details);
		echo '	<tr><td>'.$examination_blob_details['examination_id'].'</td>
				<td>'.$examination_blob_details['name'].'</td>
				<td>';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$ar_blob['fname'],
									round(strlen($ar_blob['result'])/1024,0));
				echo '</td></tr>';
	}	
		
	echo '</table>';
}

function echo_result_header()
{
	echo '<div class="basic_form">
			<div class=my_label >Examination</div>
			<div>Result</div>
			<div class=help>Unit, Ref. Intervals ,(Method)</div>';
	echo '</div>';	
}

function show_all_buttons_for_sample($link,$sample_id)
{
	$released_by=get_one_ex_result($link,$sample_id,$GLOBALS['released_by']);
	$interim_released_by=get_one_ex_result($link,$sample_id,$GLOBALS['interim_released_by']);
	if(strlen($released_by)==0 && strlen($interim_released_by)==0)		//no interim, no release, allow edit/delete no print
	{
		sample_id_prev_button($sample_id);
		sample_id_view_button($sample_id);
		sample_id_next_button($sample_id);
		sample_id_release_button($sample_id);	
		sample_id_interim_release_button($sample_id);	
		sample_id_edit_button($sample_id);
		sample_id_delete_button($sample_id);
	}
	else if(strlen($released_by)==0 && strlen($interim_released_by)!=0)	//interim but not released, so allow edit,delete,print
	{
		sample_id_prev_button($sample_id);
		sample_id_view_button($sample_id);
		sample_id_next_button($sample_id);
		sample_id_release_button($sample_id);	
		sample_id_interim_release_button($sample_id);					//allow new interim release too
		sample_id_print_button($sample_id);			
		sample_id_edit_button($sample_id);
		sample_id_delete_button($sample_id);
	}	
	else 																	//released with/without interim (so, edit/delete)
	{
		//sample_id_edit_button($sample_id);
		sample_id_prev_button($sample_id);
		sample_id_view_button($sample_id);
		sample_id_next_button($sample_id);
		//sample_id_delete_button($sample_id);
		sample_id_unrelease_button($sample_id);			
		sample_id_print_button($sample_id);			
	}
}

function view_sample($link,$sample_id)
{

	$ex_list=get_result_of_sample_in_array($link,$sample_id);
	//print_r($ex_list);
	$rblob=get_result_blob_of_sample_in_array($link,$sample_id);
	//print_r($rblob);
	$result_plus_blob_requested=$ex_list+$rblob;
	//print_r($result_plus_blob_requested);
	if(count($result_plus_blob_requested)==0)
	{
		echo '<h3>No such sample with sample_id='.$sample_id.'</h3>';
		return;
	}
	$profile_wise_ex_list=ex_to_profile($link,$result_plus_blob_requested);

	$sr=get_one_ex_result($link,$sample_id,$GLOBALS['sample_requirement']);
	//echo $sr;
	$sr_array=explode('-',$sr);
	//print_r($sr_array);
	$header=$GLOBALS[$sr_array[2]];
	echo '<H2 class="text-center only_print">'.$header['name'].'</H2>
	<H3 class="text-center only_print">'.$header['section'].'</H3>
	<H4 class="text-center only_print">'.$header['address'].'</H4>
	<H5 class="text-center only_print">'.$header['phone'].'</H5>
	<hr>
	';

	echo '<div class="basic_form">
			<div class=my_label ><span class="badge badge-primary ">Sample ID</span>
			<span class="badge badge-info"><h5>'.$sample_id.'</h5></span></div>			<div>';
			show_all_buttons_for_sample($link,$sample_id);
			echo '</div>
			<div class="help print_hide">Unique Number to get this data</div>';
	echo '</div>';	
	
	foreach($profile_wise_ex_list as $kp=>$vp)
	{
		$pinfo=get_profile_info($link,$kp);
		$div_id=$pinfo['name'].'_'.$sample_id;
		echo '<img src="img/show_hide.png" height=32 data-toggle="collapse" class=sh href=\'#'.$div_id.'\' ><div></div><div></div>';
		echo '<div class="collapse show" id=\''.$div_id.'\'>';
		echo '<h3>'.$pinfo['name'].'</h3><div></div><div></div>';
		$profile_edit_specification=json_decode($pinfo['edit_specification'],true);
		$print_style=isset($profile_edit_specification['print_style'])?$profile_edit_specification['print_style']:'';		
	
		if($print_style=='horizontal')
		{
			echo '<div class=horiz>';
			foreach($vp as $ex_id)
			{
				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$img=isset($edit_specification['img'])?$edit_specification['img']:'';
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';
				
				
				if($type!='blob')
				{
					view_field_hr($link,$ex_id,$ex_list[$ex_id]);	
				}
				else
				{
					view_field_blob_hr($link,$ex_id,$sample_id);
					if($img=='dw')
					{
						$ex_result=get_one_ex_result_blob($link,$sample_id,$ex_id);
						display_dw($ex_result,$examination_details['name']);
					}	
				}
			}
			echo '</div>';			
		}
		
		elseif($print_style=='vertical')
		{
			foreach($vp as $ex_id)
			{
				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';					
				if($type!='blob')
				{
					view_field_vr($link,$ex_id,$ex_list[$ex_id]);	
				}
				else
				{
					view_field_blob_vr($link,$ex_id,$sample_id);	
				}
			}
		}
		
		else
		{
			echo_result_header();
		
			foreach($vp as $ex_id)
			{
				
				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$img=isset($edit_specification['img'])?$edit_specification['img']:'';
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';
						
				if($type!='blob')
				{
					view_field($link,$ex_id,$ex_list[$ex_id]);	
				}
				else
				{
					view_field_blob($link,$ex_id,$sample_id);
					if($img=='dw')
					{
						$ex_result=get_one_ex_result_blob($link,$sample_id,$ex_id);
						display_dw($ex_result,$examination_details['name']);
					}
				}
			}
		}		
		echo '</div>';
	}
	
	echo '<br><footer></footer>';	
}

function view_field_blob($link,$kblob,$sample_id)
{
		$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$kblob.'\'';
		$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
		$ar_blob=get_single_row($result_blob);
	
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$kblob);
		
		//print_r($examination_blob_details);
		echo '	<div class="basic_form print_hide">
	
				<div class="my_label border border-dark ">'.$examination_blob_details['name'].'</div>
				<div>';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$ar_blob['fname']
									);
				echo '</div>';
				echo '<div  class="help border border-dark "  >Current File:'.$ar_blob['fname'].'</div>
				</div>';
}

function view_field_blob_hr($link,$kblob,$sample_id)
{
		$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$kblob.'\'';
		$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
		$ar_blob=get_single_row($result_blob);
	
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$kblob);
		
		//print_r($examination_details);
		echo '	
				<div class="print_hide">'.$examination_blob_details['name'].'
				:';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$ar_blob['fname']
									);
				echo ':'.$ar_blob['fname'].'</div>
				';
}

function view_field_blob_vr($link,$kblob,$sample_id)
{
		$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$kblob.'\'';
		$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
		$ar_blob=get_single_row($result_blob);
	
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$kblob);
		$edit_specification=json_decode($examination_blob_details['edit_specification'],true);		
		$img=isset($edit_specification['img'])?$edit_specification['img']:'';
		
		//print_r($examination_details);
		echo '	
				<div class="print_hide"><b>'.$examination_blob_details['name'].'
				:</b>';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$ar_blob['fname']
									);
				echo ':'.$ar_blob['fname'].'</div>
				';
		
		if($img=='png')
		{
			echo '<div><b>';
			echo $examination_blob_details['name'];
			echo ':</b></div>';
			echo '<div>';
			//no effect of last three parameters, not implemented
			display_png($ar_blob['result'],$ar_blob['fname'],500,200);	
			echo '</b></div>';
		}
}


function view_field_blob_vr_p($link,$kblob,$sample_id)
{
		$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$kblob.'\'';
		$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
		$ar_blob=get_single_row($result_blob);
	
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$kblob);
		$edit_specification=json_decode($examination_blob_details['edit_specification'],true);		
		$img=isset($edit_specification['img'])?$edit_specification['img']:'';
		$wd=isset($edit_specification['width'])?$edit_specification['width']:'400';
		$ht=isset($edit_specification['height'])?$edit_specification['height']:'200';
		echo '<tr><td colspan="3"><b>';
		echo $examination_blob_details['name'];
		echo ':</b></td></tr>';

		echo '<tr><td colspan="3">';
		//print_r($examination_details);
		if($img=='png')
		{
			//no effect of last three parameters, not implemented
			//width bigger than nature have no effect
			display_png_p($ar_blob['result'],$ar_blob['fname'],$wd,$ht);	
		}
		echo '</td></tr>';
}
/*
function view_sample($link,$sample_id)
{
	$ex_list=get_result_of_sample_in_array($link,$sample_id);
	$profile_wise_ex_list=ex_to_profile($link,$ex_list);
	//echo '<pre>';
	//print_r($profile_wise_ex_list);
	//echo '</pre>';
	echo '<div class="basic_form">
			<div class=my_label >Database ID:'.$sample_id.'</div>
			<div>';
				sample_id_edit_button($sample_id);
				sample_id_view_button($sample_id);
			echo '</div>
			<div class=help>Unique Number to get this data</div>';
	echo '</div>';	
	
	foreach($profile_wise_ex_list as $kp=>$vp)
	{
		$pinfo=get_profile_info($link,$kp);
		$div_id=$pinfo['name'].'_'.$sample_id;
		//echo '<h6 data-toggle="collapse" class=sh href=\'#'.$div_id.'\' >X</h6><div></div><div></div>';
		echo '<img src="img/show_hide.png" height=32 data-toggle="collapse" class=sh href=\'#'.$div_id.'\' ><div></div><div></div>';
		echo '<div class="collapse show" id=\''.$div_id.'\'>';
		echo '<h3>'.$pinfo['name'].'</h3><div></div><div></div>';
		if($pinfo['profile_id']>$GLOBALS['max_non_ex_profile'])
		{
			echo_result_header();
		}
		foreach($vp as $ex_id)
		{
			if($ex_id==$GLOBALS['mrd']){$readonly='readonly';}else{$readonly='';}
			
			view_field($link,$ex_id,$ex_list[$ex_id]);	
		}
		echo '</div>';
	}
	
	$rblob=get_result_blob_of_sample_in_array($link,$sample_id);
	//print_r($rblob);
	foreach($rblob as $kblob=>$vblob)
	{
		$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$kblob.'\'';
		$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
		$ar_blob=get_single_row($result_blob);
	
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$kblob);
		
		//print_r($examination_details);
		echo '	<div class="basic_form">
	
				<div class=my_label>'.$examination_blob_details['name'].'</div>
				<div>';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$vblob
									);
				echo '</div>';
				echo '<div  class=help  >Current File:'.$ar_blob['fname'].'</div>
				</div>';
				
	}
	echo '<br><footer></footer>';	
}
*/

function view_sample_no_profile($link,$sample_id)
{
	$sql='select * from result where sample_id=\''.$sample_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	
	echo '<div class="basic_form">';
	echo '	<div class="my_label border border-dark">ID</div>
			<div class=" border border-dark">';
			sample_id_edit_button($sample_id);
			echo '</div>
			<div class="help border border-dark">Click on ID number (green button) to edit</div>';
			
	echo '<div class="my_label border border-info  data_header">Name</div>
	<div class=" border border-info  data_header">Data</div>
	<div class="help  border border-info  data_header">Help</div>';
	while($ar=get_single_row($result))
	{
		//print_r($ar);
		$examination_details=get_one_examination_details($link,$ar['examination_id']);
		$edit_specification=json_decode($examination_details['edit_specification']);
		$h=isset($edit_specification->{'help'})?($edit_specification->{'help'}):'No help';
		//print_r($edit_specification);
		//print_r($examination_details);
		echo '	<div class="my_label border border-dark text-wrap">'.$examination_details['name'].'</div>
				<div class="border border-dark">'.$ar['result'].'</div>
				<div class="help border border-dark">'.($h).'</div>';
	}
	
	$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\'';
	$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
	while($ar_blob=get_single_row($result_blob))
	{
		//print_r($ar);
		$examination_blob_details=get_one_examination_details($link,$ar_blob['examination_id']);
		//print_r($examination_details);
		echo '	
				<div class=my_label>'.$examination_blob_details['name'].'</div>
				<div>';
				echo_download_button_two_pk('result_blob','result',
									'sample_id',$sample_id,
									'examination_id',$examination_blob_details['examination_id'],
									$sample_id.'-'.$examination_blob_details['examination_id'].'-'.$ar_blob['fname'],
									round(strlen($ar_blob['result'])/1024,0));
				echo '</div>';
				echo '<div  class=help  >Current File:'.$ar_blob['fname'].'</div>';
	}	
		
	echo '</div>';
}

function sample_id_edit_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=edit_general.php class=print_hide>
	<button class="btn btn-outline-primary btn-sm" name=sample_id value=\''.$sample_id.'\' >Edit</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=edit_general>
	</form></div>';
}


function sample_id_calculate_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=edit_general.php class=print_hide>
	<button class="btn btn-outline-primary btn-sm" name=sample_id value=\''.$sample_id.'\' >Calculate</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=calculate>
	</form></div>';
}

function sample_id_view_button($sample_id,$target='')
{
	echo '<div class="d-inline-block" ><form method=post action=view_single.php class=print_hide target=\''.$target.'\'>
	<button class="btn btn-outline-success btn-sm" name=sample_id value=\''.$sample_id.'\' >View</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=view_single>
	</form></div>';
}

function sample_id_print_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=print_single.php target=_blank class=print_hide>
	<button class="btn btn-outline-success btn-sm" name=sample_id value=\''.$sample_id.'\' >Print</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=print_single>
	</form></div>';
}


function sample_id_next_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=view_single.php  class=print_hide>
	<button class="btn btn-outline-danger btn-sm" name=sample_id value=\''.($sample_id+1).'\' >Next</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=view_single>
	</form></div>';
}


function sample_id_prev_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=view_single.php class=print_hide>
	<button class="btn btn-outline-danger btn-sm" name=sample_id value=\''.($sample_id-1).'\' >Previous</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=view_single>
	</form></div>';
}

function sample_id_delete_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=delete_sample.php class=print_hide>
	<button onclick="return confirm(\'delete really?\')" class="btn btn-outline-dark btn-sm" name=sample_id value=\''.$sample_id.'\' >Delete</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=delete_sample>
	</form></div>';
}


function sample_id_release_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=release_sample.php class=print_hide>
	<button class="btn btn-outline-secondary btn-sm" name=sample_id value=\''.$sample_id.'\' >Release</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=release_sample>
	</form></div>';
}


function sample_id_interim_release_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=interim_release_sample.php class=print_hide>
	<button class="btn btn-outline-secondary btn-sm" name=sample_id value=\''.$sample_id.'\' >Interim Release</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=interim_release_sample>
	</form></div>';
}

function sample_id_unrelease_button($sample_id)
{
	echo '<div class="d-inline-block" ><form method=post action=unrelease_sample.php class=print_hide>
	<button class="btn btn-outline-secondary btn-sm" name=sample_id value=\''.$sample_id.'\' >Un-Release</button>
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=action value=unrelease_sample>
	</form></div>';
}

function echo_download_button_two_pk($table,$field,$primary_key,$primary_key_value,$primary_key2,$primary_key_value2,$postfix='')
{
	echo '<form method=post action=download2.php class="print_hide d-inline" >
			<input type=hidden name=table value=\''.$table.'\'>
			<input type=hidden name=field value=\''.$field.'\' >
			<input type=hidden name=primary_key value=\''.$primary_key.'\'>
			<input type=hidden name=primary_key2 value=\''.$primary_key2.'\'>
			<input type=hidden name=fname_postfix value=\''.$postfix.'\'>
			<input type=hidden name=primary_key_value value=\''.$primary_key_value.'\'>
			<input type=hidden name=primary_key_value2 value=\''.$primary_key_value2.'\'>
			<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
			
			<button class="btn btn-info  btn-sm"  
			formtarget=_blank
			type=submit
			name=action
			value=download>Download</button>
		</form>';
}

function ex_to_profile($link,$ex_array)
{
	$sql='select * from profile';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$ret=array();
	while($ar=get_single_row($result))
	{
		$ex_of_profile=array_merge(
									explode(',',$ar['examination_id_list']),
									explode(',',$ar['extra'])
									);
		foreach($ex_of_profile as $v)
		{
			if(array_key_exists($v,$ex_array))
			{
				$ret[$ar['profile_id']][]=$v;
			}
		}
	}
	return $ret;
}

function copy_bin_text($link)
{
	$sql='select * from copy_bin_text';
	//echo $sql;
	$result=run_query($link,$GLOBALS['database'],$sql);
	while($ar=get_single_row($result))
	{
		//echo $ar['text'];
		echo '<span style="width: 400px;" class="text-truncate d-block" onclick="copy_to_bin(this)">'.htmlspecialchars($ar['text']).'.&#13;</span>';
	}
	
}
function edit_sample($link,$sample_id)
{
	$ex_list=get_result_of_sample_in_array($link,$sample_id);
	//print_r($ex_list);
	$rblob=get_result_blob_of_sample_in_array($link,$sample_id);
	//print_r($rblob);
	$result_plus_blob_requested=$ex_list+$rblob;
	//print_r($result_plus_blob_requested);
	$profile_wise_ex_list=ex_to_profile($link,$result_plus_blob_requested);

	//echo '<pre>';
	//print_r($profile_wise_ex_list);
	//echo '</pre>';
	echo 
	'<div class="position-fixed bg-secondary">
		<button 
		type=button
		class="btn btn-warning btn-sm p-0 m-0 d-inline"
		 data-toggle="collapse" 
		data-target="#advice" href="#advice"><img src="img/copypaste.png" width=20></button>
		<div class="p-3 collapse" id="advice">';
		echo '<p id=cb_4 onclick="clear_bin()" class="bg-danger d-inline">clear</p>
			<p id=cb_5 onclick="copy_binn()" class="bg-warning d-inline">copy</p>';
		copy_bin_text($link);	
			//<span class="d-block" id=cb_1 onclick="copy_to_bin(this)">A for apple.&#13;</span>
			//<span class="d-block" id=cb_2 onclick="copy_to_bin(this)">B for Big apple.&#13;</span>
			//<span class="d-block"  id=cb_3 onclick="copy_to_bin(this)">C for Chota apple.&#13;</span>
			echo '<textarea id=cb_ta cols=50 rows=4></textarea>';
		echo '</div>
	</div>';
		
	echo '<div class="basic_form">
			<div class=my_label ><span class="badge badge-primary ">Sample ID</span>
			<span class="badge badge-info"><h5>'.$sample_id.'</h5></span></div>
			<div>';
				sample_id_edit_button($sample_id);
				sample_id_view_button($sample_id);
				sample_id_calculate_button($sample_id);
				echo '<button class="btn btn-sm btn-warning" onclick="sync_all()">Sync All</button>';
			echo '</div>
			<div class=help>Unique Number to get this data</div>';
	echo '</div>';	
	
	foreach($profile_wise_ex_list as $kp=>$vp)
	{
		$pinfo=get_profile_info($link,$kp);
		echo '<h3>'.$pinfo['name'].'</h3><div></div><div></div>';
		foreach($vp as $ex_id)
		{
			if($ex_id==$GLOBALS['mrd'] || $ex_id==$GLOBALS['sample_requirement'] ){$readonly='readonly';}else{$readonly='';}

				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';
								
			if($type!='blob')
			{
				edit_field($link,$ex_id,$ex_list,$sample_id,$readonly);	
			}
			else
			{
				edit_blob_field($link,$ex_id,$sample_id);
			}
		}
	}

    add_get_data($link,$sample_id);
   
}

function get_result_of_sample_in_array($link,$sample_id)
{
	$sql='select * from result where sample_id=\''.$sample_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$result_array=array();
	while($ar=get_single_row($result))
	{
		$result_array[$ar['examination_id']]=$ar['result'];
	}
	//print_r($result_array);
	return $result_array;
}

function get_primary_result_of_sample_in_array($link,$sample_id)
{
	$sql='select * from primary_result where sample_id=\''.$sample_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$result_array=array();
	while($ar=get_single_row($result))
	{
		$result_array[$ar['examination_id']]=$ar['result'];
	}
	//print_r($result_array);
	return $result_array;
}

function get_result_blob_of_sample_in_array($link,$sample_id)
{
	$sql='select * from result_blob where sample_id=\''.$sample_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$result_array=array();
	while($ar=get_single_row($result))
	{
		$result_array[$ar['examination_id']]=$ar['fname'];	//no blob as result
	}
	//print_r($result_array);
	return $result_array;
}

function edit_basic($link,$result_array)//not used
{
	if(array_key_exists('1',$result_array)){$mrd=$result_array['1'];}else{$mrd='';}
	
	echo '<div id=basic class="tab-pane active">';
	echo '<div class="basic_form">';
		echo '	<label class="my_label text-danger" for="mrd">MRD</label>
				<input size=13 id=mrd name=mrd class="form-control text-danger" 
				required="required" type=text pattern="SUR/[0-9][0-9]/[0-9]{8}" placeholder="MRD"
				value=\''.$mrd.'\'>
				<p class="help"><span class=text-danger>Must have</span> 8 digit after SUR/YY/</p>';			
	echo '</div>';
	echo '</div>';
}
function delete_examination($link,$sample_id,$examination_id)
{

	$examination_details=get_one_examination_details($link,$examination_id);
	$edit_specification=json_decode($examination_details['edit_specification'],true);
	if(!$edit_specification){$edit_specification=array();}
	
	$type=isset($edit_specification['type'])?$edit_specification['type']:'text';
	
	if($type=='blob')
	{
		$sql='DELETE FROM `result_blob`
          WHERE `sample_id` = \''.$sample_id.'\' AND `examination_id` = \''.$examination_id.'\'';
	}
	else
	{
		$sql='DELETE FROM `result`
          WHERE `sample_id` = \''.$sample_id.'\' AND `examination_id` = \''.$examination_id.'\'';
	}
		$result=run_query($link,$GLOBALS['database'],$sql);
		//echo $sql;
		if($result==false)
			{
					echo '<h3 style="color:green;"> record not Deleted</h3>';
			}
			else
			{
					echo '<h3 style="color:green;"> '.rows_affected($link).' records  deleted</h3>';
			}
		
}

function get_primary_result($link,$sample_id,$examination_id)
{
	$sql='select * from primary_result where sample_id=\''.$sample_id.'\' and examination_id=\''.$examination_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$result_array=array();
	
	$values='';
	while($ar=get_single_row($result))
	{
		//$values=$values.$ar['result'].',';
		$element_id='pr_id_'.$sample_id.'_'.$examination_id;
		echo '<button onclick="sync_result(this)"
					class="btn btn-sm btn-outline-dark  no-gutters align-top"
					id=\''.$element_id.'\' 
					data-sid=\''.$sample_id.'\' 
					data-exid=\''.$examination_id.'\' 
					value=\''.$ar['result'].'\' >'.$ar['result'].'</button>';
	}
	//return $values;
}

//used to supply default
//calls sync_with_that() from project_common.js
function show_source_button($link_element_id,$my_value)
{
	$element_id='source_for_'.$link_element_id;
	echo '<button onclick="sync_with_that(this,\''.$link_element_id.'\')"
				type=button
				class="btn btn-sm btn-outline-dark  no-gutters align-top"
				id=\''.$element_id.'\' 
				value=\''.$my_value.'\'>'.$my_value.'</button>';
}

function get_primary_result_blob($link,$sample_id,$examination_id)
{
	$sql='select * from primary_result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$examination_id.'\'';
	//echo $sql;
	$result=run_query($link,$GLOBALS['database'],$sql);
	$result_array=array();
	
	$values='';
	while($ar=get_single_row($result))
	{
		//$values=$values.$ar['result'].',';
		$element_id='pr_id_'.$sample_id.'_'.$examination_id;
		echo '<button onclick="sync_result_blob(this)"
					class="btn btn-sm btn-outline-dark  no-gutters align-top"
					id=\''.$element_id.'\' 
					data-sid=\''.$sample_id.'\' 
					data-type=\'blob\' 
					data-exid=\''.$examination_id.'\' 
					data-uniq=\''.$ar['uniq'].'\' 
					value=\''.$ar['uniq'].'\' >'.$ar['uniq'].'</button>';
	}
	//return $values;
}

function show_calculate_button($link,$sample_id,$examination_id,$equation)
{
	$target_element_id='r_id_'.$sample_id.'_'.$examination_id;
	
	$this_element_id='cal_for_'.$target_element_id;
	echo '<button onclick="calcuate_for_target(this,\''.$target_element_id.'\',\''.$equation.'\')"
				type=button
				class="btn btn-sm btn-outline-dark  no-gutters align-top"
				id=\''.$this_element_id.'\' 
				value=\''.$equation.'\'>'.$equation.'</button>';
}

function calculate_result($link,$equation,$ex_list,$sample_id,$decimal=0)
{
	//check devide by zero,  e is not allowed to have 0
	//check if ex result is empty
	//echo $equation;
	$data=explode(',',$ex_list);
	$data_count=count($data);
	//print_r($data);
	$eq=$equation;
	$eq_length=strlen($eq);
	
	$parameter=0;
	
	$ret='';
	for($i=0;$i<$eq_length;$i++)
	{
		if($eq[$i]=='E')
		{		
			$ex_result=get_one_ex_result($link,$sample_id,$data[$parameter]);
			//echo $data[$parameter].'-result = '.$ex_result;
			$ret=$ret.$ex_result;
			$parameter++;
		}
		elseif($eq[$i]=='e')
		{		
			$ex_result=get_one_ex_result($link,$sample_id,$data[$parameter]);
			if($ex_result>0)
			{
				//echo $ex_result;
				$ret=$ret.$ex_result;
				$parameter++;
			}
			else
			{
				//echo $data[$parameter].'-result = 0';
				return false;
			}
		}
		else{$ret=$ret.$eq[$i];}
	}
	echo 'round('.$ret.','.$decimal.')<br>';
	return trim(shell_exec('calc "round('.$ret.','.$decimal.')"'));
	//$evaluator = new \Matex\Evaluator();
	
	//try
	//{
		//return round($evaluator->execute($ret),$decimal);
	//}
	//catch( \exception $e )
	//{
		//return $e->getMessage();
	//}
	
}


function edit_field($link,$examination_id,$result_array,$sample_id,$readonly='')
{
	if(array_key_exists($examination_id,$result_array)){$result=$result_array[$examination_id];}else{$result='';}
	$examination_details=get_one_examination_details($link,$examination_id);
	$edit_specification=json_decode($examination_details['edit_specification'],true);
	if(!$edit_specification){$edit_specification=array();}
	
	$type=isset($edit_specification['type'])?$edit_specification['type']:'text';
	$readonly=isset($edit_specification['readonly'])?$edit_specification['readonly']:'';
	$help=isset($edit_specification['help'])?$edit_specification['help']:'';
	$pattern=isset($edit_specification['pattern'])?$edit_specification['pattern']:'';
	$placeholder=isset($edit_specification['placeholder'])?$edit_specification['placeholder']:'';
	$step=isset($edit_specification['step'])?$edit_specification['step']:0;
	$zoom=isset($edit_specification['zoom'])?$edit_specification['zoom']:'';
	
	
	$element_id='r_id_'.$sample_id.'_'.$examination_id;
	if($type=='yesno')
	{
				//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block  no-gutters">';
					echo '
					<button 
						'.$readonly.'
					id="'.$element_id.'" 
						name="'.$examination_id.'" 
						data-exid="'.$examination_id.'" 
						data-sid="'.$sample_id.'" 
						data-user="'.$_SESSION['login'].'" 
						class="form-control btn btn-info mb-1 autosave-yesno"
						value=\''.$result.'\'
						type=button
						>'.$result.'</button>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
						get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	else if($type=='select')
	{
		$option=isset($edit_specification['option'])?explode(',',$edit_specification['option']):array();
		$option_html='';
		
		foreach($option as $v)
		{
			if($v==$result)
			{
				$option_html=$option_html.'<option selected>'.$v.'</option>';
			}
			else
			{
				$option_html=$option_html.'<option>'.$v.'</option>';
			}
		}
		
				//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block  no-gutters">';	
				
			echo '
					<select '.$readonly.' 
					id="'.$element_id.'" 
						name="'.$examination_id.'" 
						data-exid="'.$examination_id.'" 
						data-sid="'.$sample_id.'" 
						data-user="'.$_SESSION['login'].'" 
						class="form-control autosave-select">'.$option_html.'</select>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	
	elseif($type=='number')
	{
		$decimal=isset($edit_specification['decimal'])?$edit_specification['decimal']:0;
		$calculate=isset($edit_specification['calculate'])?$edit_specification['calculate']:'';	
		$ex_list=isset($edit_specification['ex_list'])?$edit_specification['ex_list']:'';	
		//if(strlen($calculate)>0)
		//{
			//$result=calculate_result($link,$calculate,$sample_id,$decimal);
		//}
				//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block  no-gutters">';	
				
			echo '
					<input 
						'.$readonly.'
					id="'.$element_id.'" 
						name="'.$examination_id.'" 
						data-exid="'.$examination_id.'" 
						data-sid="'.$sample_id.'" 
						data-user="'.$_SESSION['login'].'" 
						class="form-control autosave" 
						type=\''.$type.'\' 
						step=\''.$step.'\' 
						value=\''.$result.'\'>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
					if(strlen($calculate)>0)
					{
						//show_source_button($element_id,calculate_result($link,$calculate,$ex_list,$sample_id,$decimal));
					}
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	elseif($type=='date' || $type=='time')
	{
		//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block  no-gutters">';			
			echo '
						<input 
						'.$readonly.'
					id="'.$element_id.'" 
						name="'.$examination_id.'" 
						data-exid="'.$examination_id.'" 
						data-sid="'.$sample_id.'" 
						data-user="'.$_SESSION['login'].'" 
						class="form-control autosave" 
						type=\''.$type.'\' 
						value=\''.$result.'\'>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	elseif($type=='datetime-local')
	{
		$step=isset($edit_specification['step'])?$edit_specification['step']:1;
		//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block  no-gutters">';
			echo '
						<input 
						'.$readonly.'
					id="'.$element_id.'" 
						name="'.$examination_id.'" 
						data-exid="'.$examination_id.'" 
						data-sid="'.$sample_id.'" 
						data-user="'.$_SESSION['login'].'" 
					pattern="'.$pattern.'" 
						class="form-control autosave" 
						type=\''.$type.'\' 
						value=\''.$result.'\'>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	elseif($type=='blob')
	{
		edit_blob_field($link,$examination_id,$sample_id);
	} 

	elseif($type=='json')
	{
		//////
		
		$json=isset($edit_specification['json'])?$edit_specification['json']:'';
		//$json_array=json_decode($json,true);
		//$type=isset($edit_specification['type'])?$edit_specification['type']:'text';
				
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block no-gutters">';
					//print_r($json_array);
					echo '<pre>';print_r($edit_specification['json']);echo '</pre>';
					echo '<textarea rows=1
					'.$readonly.'
					id="'.$element_id.'" 
					name="'.$examination_id.'" 
					data-exid="'.$examination_id.'" 
					data-sid="'.$sample_id.'" 
					data-user="'.$_SESSION['login'].'" 
					pattern="'.$pattern.'" 
					class="form-control autosave p-0 m-0 no-gutters" 
					type=\''.$type.'\' >'.
					htmlspecialchars($result,ENT_QUOTES).'</textarea>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	}
	 else  if($type=='subsection')
	{
		//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable_subsection($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block no-gutters">';
				echo '<textarea rows=1
					'.$readonly.'
					id="'.$element_id.'" 
					name="'.$examination_id.'" 
					data-exid="'.$examination_id.'" 
					data-sid="'.$sample_id.'" 
					data-user="'.$_SESSION['login'].'" 
					pattern="'.$pattern.'" 
					class="form-control autosave p-0 m-0 no-gutters" 
					type=\''.$type.'\' >'.
					htmlspecialchars($result,ENT_QUOTES).'</textarea>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	} 
	else  
	{
		//////
		echo '<div class="basic_form  m-0 p-0 no-gutters">';
			////
			set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
			////
			echo '<div class="m-0 p-0 no-gutters">';
				////
				echo '<div class="d-inline-block no-gutters">';
				echo '<textarea rows=1 
					'.$readonly.'
					id="'.$element_id.'" 
					name="'.$examination_id.'" 
					data-exid="'.$examination_id.'" 
					data-sid="'.$sample_id.'" 
					data-user="'.$_SESSION['login'].'" 
					pattern="'.$pattern.'" 
					class="form-control autosave p-0 m-0 no-gutters '.$zoom.' " 
					style="resize: both;"
					type=\''.$type.'\' >'.
					htmlspecialchars($result,ENT_QUOTES).'</textarea>';
				echo '</div>';
				echo '<div class="d-inline  no-gutters">';
					get_primary_result($link,$sample_id,$examination_id);
				echo '</div>';
			echo '</div>';
			echo '<div class="help"><pre>'.$help.'</pre></div>';	
		echo '</div>';
	} 
}

/*
function decide_alert($result,$interval)
{
	if(strlen($interval)==0){return '';}
	if(strlen($result)==0){return '';}
	$is=explode('-',$interval);
	//100-1000-4000-11000-20000-200000
	if($result<$is[2]) //below ref
	{
		if($result<$is[1])	//below critical
		{
			if($result<$is[0])	//below absurd
			{
				return '<<<Absurd Low>>>';
			}
			else
			{
				return '<<<Critical Low>>>';
			}
		}
		else
		{
			return '<<<Abnormal Low>>>';
		}
	}
	elseif($result>$is[3])
	{
		if($result>$is[4])
		{
			if($result>$is[5])
			{
				return '('.$result.'>'.$is[5].')<<<Absurd High>>>';
			}
			else
			{
				return '<<<Critical High>>>';
			}
		}
		else
		{
			return '<<<Abnormal High>>>';
		}
	}
	else
	{
		return '';
	}	
}
*/

function decide_alert($result,$interval_l,$cinterval_l,$ainterval_l,$interval_h,$cinterval_h,$ainterval_h)
{
	if(strlen($interval_l)==0 && strlen($cinterval_l)==0 && strlen($ainterval_l)==0 &&
	strlen($interval_h)==0 && strlen($cinterval_h)==0 && strlen($ainterval_h)==0){return '';}
	if(strlen($result)==0){return '';}
		
	if(is_numeric($ainterval_l))
	{
		if($result<$ainterval_l)
		{
			return $alert='<--Absurd Low';
			//return $alert='<--'.$result.'<'.$ainterval_l.' Absurd Low';
		}
	}

	if(is_numeric($ainterval_h))
	{
		if($result>$ainterval_h)
		{
			return $alert='<--Absurd High';
			//return $alert='<--'.$result.'>'.$ainterval_h.' Absurd high';
		}
		
	}

	if(is_numeric($cinterval_l))
	{
		if($result<$cinterval_l)
		{
			return $alert='<--Critical Low';
			//return $alert='<--'.$result.'<'.$cinterval_l.' Critical Low';

		}
	}

	if(is_numeric($cinterval_h))
	{
		if($result>$cinterval_h)
		{
			//return $alert='<--'.$result.'>'.$cinterval_h.' Critical High';
			return $alert='<--Critical High';
		}
	}


	if(is_numeric($interval_l))
	{
		if($result<$interval_l)
		{
			//return $alert='<--'.$result.'<'.$interval_l.' Abnormal Low';
			return $alert='<--Abnormal Low';
		}
	}

	if(is_numeric($interval_h))
	{
		if($result>$interval_h)
		{
			//return $alert='<--'.$result.'>'.$interval_h.' Abnormal high';
			return $alert='<--Abnormal High';
		}
	}

	return '';			
}

function display_dw($ex_result,$label='')
{
	$ar=unpack('C*', $ex_result);

	//$arr=str_split($ex_result);
	//$an=array();
	//$counter=0;
	//$max=count($arr);
	
	//echo '<table border=1>';
	//foreach($arr as $kk=>$vv)
	//{
		
		//echo '<tr><td>'.$kk.'</td><td>'.$vv.'</td><td>'.ord($vv).'</td>
		//<td style="font-size:4px">';
		//for($i=0;$i<(int)(ord($vv))-32;$i++)
		//{
			//echo 'o';
		//}
		//echo '</td>
		//</tr>';
	//}
	//echo '</table>';
//echo '<pre>';print_r($an);print_r($ar);print_r($arr);
	$width=256; //128 X 2
    $height=128; //256;//223+32=255 make is half to save space
    $im = imagecreatetruecolor($width,$height);
    $white = imagecolorallocate($im, 255, 255, 225);
    $black = imagecolorallocate($im, 0,0,0);
	imagefill($im,0,0,$white);
	imagestring($im, 5, 3, 1, $label, $black);
	$px=0;
	$py=256;
	$length=count($ar);
	
	//for($p=1;$p<$length;$p=$p+2)
	//{
		//$y=$ar[$p]+$ar[$p+1];
		//$x=$p*2;
		////imagesetpixel ( $im , $x , $y , $black );
		//imageline ( $im , $x , 0 , $x , $y-64 , $black ) ;

	//}
	//foreach ($ar as $k=>$v)
	//{
		////Micros-60
		////base line=space=0x20=32
		////max amplitude=223 (223+32=255)
		//$y=(256-$v)/2 +16; //make half add 16 to get baseline
		////$y=$v/2 +16; //make half add 16 to get baseline
		//$x=$k*2;	//every two pixel
		////imagesetpixel ( resource $image , int $x , int $y , int $color ) 
		////imagesetpixel ( $im , $x , $y , $black );
		//imageline ( $im , $px , $py , $x , $y , $black ) ;
		//$py=$y;
		//$px=$x;
	//}

	foreach ($ar as $k=>$v)
	{
		//Micros-60
		//base line=space=0x20=32
		//max amplitude=223 (223+32=255)
		$y=(256-$v)/2 +16; //make half add 16 to get baseline
		$x=$k*2;	//every two pixel
		imageline ( $im , $x , 128 , $x , $y , $black ) ;
	}	
	ob_start();	
	imagepng($im);
	$myStr = ob_get_contents();
	ob_end_clean();
	
	echo "<img src='data:image/png;base64,".base64_encode($myStr)."'/>";
	imagedestroy($im);	

}



function view_field($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$type=isset($edit_specification['type'])?$edit_specification['type']:'';
		$interval_l=isset($edit_specification['interval_l'])?$edit_specification['interval_l']:'';
		$cinterval_l=isset($edit_specification['cinterval_l'])?$edit_specification['cinterval_l']:'';
		$ainterval_l=isset($edit_specification['ainterval_l'])?$edit_specification['ainterval_l']:'';
		$interval_h=isset($edit_specification['interval_h'])?$edit_specification['interval_h']:'';
		$cinterval_h=isset($edit_specification['cinterval_h'])?$edit_specification['cinterval_h']:'';
		$ainterval_h=isset($edit_specification['ainterval_h'])?$edit_specification['ainterval_h']:'';
		$img=isset($edit_specification['img'])?$edit_specification['img']:'';
		
		if($img=='dw')
		{
			echo '<div class="basic_form " id="ex_'.$ex_id.'">';
			echo '	<div class="my_label border border-dark text-wrap">'.$examination_details['name'].'</div>
				<div class="border border-dark"><pre class="m-0 p-0 border-0">';
			display_dw($ex_result);
			echo '</pre></div>';							
			echo '<div class="help border border-dark"><pre style="border-color:white">'.$help.'</pre></div>';
			echo '</div>';			
		}
		elseif($type=='subsection')
		{
			echo '<div class="basic_form " id="ex_'.$ex_id.'">';
			echo '	<div class="my_label border border-dark text-wrap"></h3></div>
				<div class="border border-dark">
				<h3 class="text-center">'.$examination_details['name'].'</h3>
				</div>
				<div class="help border border-dark"><pre style="border-color:white">'.$help.'</pre></div>';
			echo '</div>';
		}

		else
		{
			echo '<div class="basic_form " id="ex_'.$ex_id.'">';
			echo '	<div class="my_label border border-dark text-wrap">'.$examination_details['name'].'</div>
				<div class="border border-dark"><pre class="m-0 p-0 border-0">'.
					htmlspecialchars($ex_result.' '.
					decide_alert($ex_result,$interval_l,$cinterval_l,$ainterval_l,$interval_h,$cinterval_h,$ainterval_h)).'</pre></div>
				<div class="help border border-dark"><pre style="border-color:white">'.$help.'</pre></div>';
			echo '</div>';
		}
		
}				


function view_field_hr($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$interval_l=isset($edit_specification['interval_l'])?$edit_specification['interval_l']:'';
		$cinterval_l=isset($edit_specification['cinterval_l'])?$edit_specification['cinterval_l']:'';
		$ainterval_l=isset($edit_specification['ainterval_l'])?$edit_specification['ainterval_l']:'';
		$interval_h=isset($edit_specification['interval_h'])?$edit_specification['interval_h']:'';
		$cinterval_h=isset($edit_specification['cinterval_h'])?$edit_specification['cinterval_h']:'';
		$ainterval_h=isset($edit_specification['ainterval_h'])?$edit_specification['ainterval_h']:'';
						
		echo '<div id="ex_'.$ex_id.'"><pre><b>'.$examination_details['name'].':</b>'.
					htmlspecialchars($ex_result).' '.				
					decide_alert($ex_result,$interval_l,$cinterval_l,$ainterval_l,$interval_h,$cinterval_h,$ainterval_h).'</pre>';
		echo '</div>';
}				

function edit_blob_field($link,$examination_id,$sample_id)
{
	//get examination details
	
	$examination_details=get_one_examination_details($link,$examination_id);
	//get result_blob details
	$sql_blob='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$examination_id.'\' ';
	$result_blob=run_query($link,$GLOBALS['database'],$sql_blob);
	//$ar_blob=get_single_row($result_blob);

	$element_id='r_id_'.$sample_id.'_'.$examination_id;

	echo '<div class="basic_form">';
	set_lable($_POST['session_name'],$_POST['sample_id'],$examination_details,$examination_id);
	//echo '	<div class=my_label>'.$examination_details['name'].'</div>
	echo'<div class="border ">';	
	
	if(get_row_count($result_blob)>0)
	{
		$ar_blob=get_single_row($result_blob);
		echo_download_button_two_pk('result_blob','result',
								'sample_id',$sample_id,
								'examination_id',$examination_details['examination_id'],
								$sample_id.'-'.$examination_details['examination_id'].'-'.$ar_blob['fname'],
								round(strlen($ar_blob['result'])/1024,0));
	}
	echo_upload_two_pk($sample_id,$examination_id);	
	echo '<input type=hidden
					id="'.$element_id.'" 
					name="'.$examination_id.'" 
					data-exid="'.$examination_id.'" 
					data-sid="'.$sample_id.'" 
					data-type="blob" 
					data-user="'.$_SESSION['login'].'" 
					class="form-control autosave-blob p-0 m-0 no-gutters" 
					>';
	get_primary_result_blob($link,$sample_id,$examination_id);
						
	//echo
	echo '</div>';
	if(isset($ar_blob['fname']))
	{
		echo '<div  class=help  >Current File:'.$ar_blob['fname'].'</div>';
	}
	echo '</div>';
}

function echo_upload_two_pk($sample_id,$examination_id)
{
	echo '<form method=post enctype="multipart/form-data">';
	echo '<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>';
	echo '<input type=hidden readonly size=8  name=examination_id value=\''.$examination_id.'\'>';
	echo '<input type=hidden name=sample_id value=\''.$sample_id.'\'>';		
	echo '<input type=file name=fvalue >';
	echo '<button  class="btn btn-success" type=submit name=action value=upload>Upload</button>';
	echo'</form>';
}

function file_to_str($link,$file)
{
	if($file['size']>0)
	{
		$fd=fopen($file['tmp_name'],'r');
		$size=$file['size'];
		$str=fread($fd,$size);
		return my_safe_string($link,$str);
	}
	else
	{
		return false;
	}
}

function save_result_blob($link)
{
		$blob=file_to_str($link,$_FILES['fvalue']);
		if(strlen($blob)!=0)
		{
		$sql='update result_blob 
				set 
					fname=\''.$_FILES['fvalue']['name'].'\'	,
					result=\''.$blob.'\'	
				where 
					sample_id=\''.$_POST['sample_id'].'\' 
					and
					examination_id=\''.$_POST['examination_id'].'\'';
		//echo $sql;
			if(!$result=run_query($link,$GLOBALS['database'],$sql))
			{
				echo '<br>Data not updated';
			}
			else
			{
				echo '<p>'.$_FILES['fvalue']['name'].' Saved</p>';				
			}	
		}
		else
		{
			echo '<p>0 size file. data not updated</p>';				
		}
}


function get_basic()
{
	$YY=strftime("%y");

echo '<div id=basic class="tab-pane active">';
echo '<div class="basic_form">';
	echo '	<label class="my_label text-danger" for="mrd">MRD</label>
			<input size=13 id=mrd name=mrd class="form-control text-danger" required="required" type=text pattern="SUR/[0-9][0-9]/[0-9]{8}" placeholder="MRD" value="SUR/'.$YY.'/"\>
			<p class="help"><span class=text-danger>Must have</span> 8 digit after SUR/YY/</p>';		
echo '</div>';
echo '</div>';	

}

function get_more_basic()
{

echo '<div id=more_basic class="tab-pane ">'; //donot mix basic_form(grid) with bootsrap class
echo '<div class="basic_form">';
	echo '	<label  class="my_label"  for="department">Department:</label>';
			mk_select_from_array('department',$GLOBALS['department']);
			echo '<p class="help">Select Department</p>';
			
	echo '	<label  class="my_label"  for="unit">Unit</label>';
			mk_select_from_array('unit',$GLOBALS['unit']);
			echo '<p class="help">Select Unit</p>';
			
	echo '	<label  class="my_label"  for="location3">Ward/OPD</label>
			<div class="form-control">
					<label class="radio-inline"><input type="radio" name="wardopd" value=OPD >OPD</label>
					<label class="radio-inline"><input type="radio" name="wardopd" value=Ward >Ward</label>
			</div>
			<p class="help">Ward/OPD</p>';
			
	echo '	<label  class="my_label"  for="ow_no">OPD/Ward No:</label>';
			mk_select_from_array('ow_no',$GLOBALS['ow_no']);
			echo '<p class="help">OPD/Ward Number</p>';

			
	echo '	<label  class="my_label" for="unique_id">AADHAR:</label>
			<input class="form-control" type=text id=unique_id name=unique_id placeholder=AADHAR>
			<p class="help">Full 12 Digit AADHAR number</p>';

	echo '	<label  class="my_label" for="unique_id">Mobile</label>
			<input class="form-control" type=text id=mobile name=mobile placeholder=Mobile>
			<p class="help">10 digit Mobile number</p>';
						
	echo '	<label  class="my_label" for="sex">Sex:</label>
			<select class="form-control" id=sex name=sex><option></option><option>M</option><option>F</option><option>O</option></select>
			<p class="help"> O for others</p>';
			
	echo '	<label   class="my_label" for="dob">DOB:</label>
			<input type=date id=dob name=dob>
			<p class="help">Approximate DOB</p>';

	echo '	<label  class="my_label" for="age">Age</label>
			<input class="form-control" type=text id=age name=age placeholder=Age>
			<p class="help">Write age in what ever way you like</p>';
			
	echo '	<label  class="my_label"  for="extra">Extra:</label>
			<input class="form-control" type=text id=extra name=extra placeholder=Extra>
			<p class="help">Any other extra details</p>';
echo '</div>';
echo '</div>';

}


function get_data($link)
{
	echo '<form method=post class="bg-light jumbotron">';
	echo '<input type=hidden name=session_name value=\''.session_name().'\'>';

	echo '<ul class="nav nav-pills nav-justified">
			<li class="active" ><button class="btn btn-secondary" type=button data-toggle="tab" href="#basic">Basic</button></li>
			<li><button class="btn btn-secondary" type=button  data-toggle="tab" href="#examination">Examinations</button></li>
			<li><button class="btn btn-secondary" type=button  data-toggle="tab" href="#profile">Profiles</button></li>
			<li><button class="btn btn-secondary" type=button  data-toggle="tab" href="#super_profile">SuperProfiles</button></li>
			<li><button type=submit class="btn btn-primary form-control" name=action value=insert>Save</button></li>
		</ul>';
	echo '<div class="tab-content">';
		get_basic();
		get_examination_data($link);
		get_profile_data($link);
		get_super_profile_data($link);
	echo '</div>';

	echo '</form>';			
}
function add_get_data($link,$sample_id)
{
		
	echo '<form method=post class="bg-light">';
	echo '<input type=hidden name=session_name value=\''.session_name().'\'>';
   echo '<input type=hidden name=sample_id value=\''.$sample_id.'\'>';
   echo'<div class="text-info"><h3>Insert New Fields</h3></div>';
	echo '<ul class="nav nav-pills nav-justified">
			<li><button class="btn btn-secondary" type=button  data-toggle="tab" href="#examination">Examinations</button></li>
			<li><button class="btn btn-secondary" type=button  data-toggle="tab" href="#profile">Profiles</button></li>
			<li><button type=submit class="btn btn-primary form-control" name=action value=insert>Save</button></li>
		</ul>';
	echo '<div class="tab-content">';
		get_examination_data($link);
		get_profile_data($link);
	echo '</div>';

	echo '</form>';			
}

/*
function get_examination_data($link)
{
	$sql='select * from examination';
	$result=run_query($link,$GLOBALS['database'],$sql);
	echo '<div id=examination class="tab-pane">';
	echo '<div class="ex_profile">';
	while($ar=get_single_row($result))
	{
		my_on_off_ex($ar['name'],$ar['examination_id']);
	}
	echo '<input type=text name=list_of_selected_examination id=list_of_selected_examination>';
	echo '</div>';
	echo '</div>';
}
*/

function get_examination_data($link)
{
	$sql='select * from profile';
	$result=run_query($link,$GLOBALS['database'],$sql);

	echo '<div id=examination class="tab-pane">';

	while($ar=get_single_row($result))
	{
		$pinfo=get_profile_info($link,$ar['profile_id']);

		$div_id=$pinfo['name'];
		echo '<img src="img/show_hide.png" height=32 data-toggle="collapse" class=sh href=\'#'.$div_id.'\' ><div></div><div></div>';
		echo '<div class="collapse show " id=\''.$div_id.'\'>';
			echo '<h3>'.$pinfo['name'].'</h3>';
			echo '<div class="ex_profile">';
				$ex_list=array_merge(explode(',',$ar['examination_id_list']),explode(',',$ar['extra']));
				//print_r(explode(',',$ar['examination_id_list']));
				//print_r(explode(',',$ar['extra']));
				$ex_list=array_filter($ex_list);
				//print_r($ex_list);
				foreach($ex_list as $v)
				{
					$ex_data=get_one_examination_details($link,$v);
					$sr=$ex_data['sample_requirement']!='None'?$ex_data['sample_requirement']:'';
					my_on_off_ex($ex_data['name'].'<br>'.$sr,$ex_data['examination_id']);
				}
			echo '</div>';
		echo '</div>';
	}
	echo '<input type=text readonly name=list_of_selected_examination id=list_of_selected_examination>';
	echo '</div>';
}

function get_profile_data($link)
{
	$sql='select * from profile';
	$result=run_query($link,$GLOBALS['database'],$sql);
	echo '<div id=profile  class="tab-pane">';
	echo '<div class="ex_profile">';
	while($ar=get_single_row($result))
	{
		my_on_off_profile($ar['name'],$ar['profile_id']);
	}
	echo '<input type=text readonly name=list_of_selected_profile id=list_of_selected_profile>';
	echo '</div>';
	echo '</div>';
}

function get_super_profile_data($link)
{
	$sql='select * from super_profile';
	$result=run_query($link,$GLOBALS['database'],$sql);
	echo '<div id=super_profile  class="tab-pane">';
	echo '<div class="ex_profile">';
	while($ar=get_single_row($result))
	{
		my_on_off_super_profile($ar['name'],$ar['super_profile_id']);
	}
	echo '<input type=text readonly name=list_of_selected_super_profile id=list_of_selected_super_profile>';
	echo '</div>';
	echo '</div>';
}

function get_profile_info($link,$profile_id)
{
	$sql='select * from profile where profile_id=\''.$profile_id.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	return get_single_row($result);
}

function get_examination_blob_data($link)
{
	$sql='select * from examination where examination_id>10000';
	$result=run_query($link,$GLOBALS['database'],$sql);
	echo '<div id="examination_blob" class="tab-pane ">';
	while($ar=get_single_row($result))
	{
		my_on_off_ex_blob($ar['name'],$ar['examination_id']);
	}
	echo '<input type=text name=list_of_selected_examination_blob id=list_of_selected_examination_blob>';
	echo '</div>';
}

function my_on_off_ex($label,$id)
{
	
	echo '<button 
			class="btn btn-sm btn-outline-primary"
			type=button 
			onclick="select_examination_js(this, \''.$id.'\',\'list_of_selected_examination\')"
			>'.$label.'</button>';
}
function my_on_off_ex_blob($label,$id)
{
	
	echo '<button 
			class="btn btn-sm btn-outline-primary"
			type=button 
			onclick="select_examination_blob_js(this, \''.$id.'\',\'list_of_selected_examination_blob\')"
			>'.$label.'</button>';
}
function my_on_off_profile($label,$id)
{
	
	echo '<button 
			class="btn btn-sm btn-outline-primary"
			type=button 
			onclick="select_profile_js(this, \''.$id.'\',\'list_of_selected_profile\')"
			>'.$label.'</button>';
}
function my_on_off_super_profile($label,$id)
{
	
	echo '<button 
			class="btn btn-sm btn-outline-primary"
			type=button 
			onclick="select_super_profile_js(this, \''.$id.'\',\'list_of_selected_super_profile\')"
			>'.$label.'</button>';
}

function show_sample_required($sar)
{
	//print_r($sar);
	echo '<h5 class="text-dark">Required Samples with alloted Sample ID are as follows</h5>';
	foreach($sar as $k=>$v)
	{
		echo '<h5 ><span class="text-success">'.$k.'</span>:<span class="text-primary">'.$v.'</span></h5>';
	}
}
//find ex
//find sample req for each
//get unique 

function convert_super_profile_to_profile($link,$super_profile_csv)
{
	$super_profile_requested=explode(',',$super_profile_csv);
	$profile_requested_in_super_profile=array();
	foreach($super_profile_requested as $sp)
	{
		$psql='select * from super_profile where super_profile_id=\''.$sp.'\'';
		$result=run_query($link,$GLOBALS['database'],$psql);
		$ar=get_single_row($result);
		if(isset($ar['profile_id_list']))
		{
			$profile_requested=explode(',',$ar['profile_id_list']);
			$profile_requested_in_super_profile=array_merge($profile_requested_in_super_profile,$profile_requested);
		}
	}
	return $profile_requested_in_super_profile;
}

function save_insert($link)
{
			//find list of super_profiles requested, merge with profiles requested,then..
			//find list of examinations requested
			//determine sample-type required
			//find sample_id to be given
			//insert all examinations/non-examinations in result table
			
	//find list of examinations requested//////////////////////////////
	$requested=array();
	if(isset($_POST['mrd'])){$requested[]=$GLOBALS['mrd'];} //makesure it is always available
	
	$ex_requested=array_filter(explode(',',$_POST['list_of_selected_examination']));
	$requested=array_merge($requested,$ex_requested);
	//echo '<pre>following is requested:<br>';print_r($requested);echo '</pre>';
	
	$profile_requested=explode(',',$_POST['list_of_selected_profile']);
	$profile_requested_in_super_profile=convert_super_profile_to_profile($link,$_POST['list_of_selected_super_profile']);
	$profile_requested=array_unique(array_merge($profile_requested,$profile_requested_in_super_profile));

//0	
	//echo '<pre>following profiles are requested:<br>';print_r($profile_requested);echo '</pre>';
	
	foreach($profile_requested as $value)
	{
		$psql='select * from profile where profile_id=\''.$value.'\'';
		$result=run_query($link,$GLOBALS['database'],$psql);
		$ar=get_single_row($result);
		$profile_ex_requested_main=explode(',',$ar['examination_id_list']);
		
		$profile_ex_requested=$profile_ex_requested_main;
		$requested=array_merge($requested,$profile_ex_requested);
	}

	$requested=array_filter(array_unique($requested));
//1	
	//echo '<pre>following is requested:<br>';print_r($requested);echo '</pre>';

	//determine sample-type required for each and also distinct types////////////////////////////////////
	$sample_required=array();
	//echo '<pre>following samples are required:<br>';print_r($sample_required);echo '</pre>';
	$stype_for_each_requested=array();
	
	foreach($requested as $ex)
	{
		$psql='select sample_requirement from examination where examination_id=\''.$ex.'\'';
		//echo $psql.'<br>';
		$result=run_query($link,$GLOBALS['database'],$psql);
		$ar=get_single_row($result);
		$sample_required[]=$ar['sample_requirement'];
		$stype_for_each_requested[$ex]=$ar['sample_requirement'];
		//echo '<pre>following samples are required:<br>';print_r($sample_required);echo '</pre>';
	}

//2	
	//echo '<pre>following are sample_requirements for each:<br>';print_r($stype_for_each_requested);echo '</pre>';
	//echo '<pre>following samples are required:<br>';print_r($sample_required);echo '</pre>';
	
	$sample_required=array_unique($sample_required);
//3	
	//echo '<pre>following samples are required:<br>';print_r($sample_required);echo '</pre>';
	
	//determine sample_id to be given/////////////////////////////////
	$sample_id_array=set_sample_id($link,$sample_required);
//4	
	//echo '<pre>following samples ids are alloted:<br>';print_r($sample_id_array);echo '</pre>';
	show_sample_required($sample_id_array);
//insert examinations////////////////////////////////////////////
	
	foreach($sample_id_array as $stype=>$sid)
	{
		foreach($stype_for_each_requested as $ex=>$exreq)
		{
			$examination_details=get_one_examination_details($link,$ex);
			$edit_specification=json_decode($examination_details['edit_specification'],true);
			$type=isset($edit_specification['type'])?$edit_specification['type']:'';
					
				
				
			//echo $ex.'<br>';
			if($stype==$exreq)
			{
				if($type!='blob')
				{
					insert_one_examination_without_result($link,$sid,$ex);
				}
				else
				{
					//echo 'blob<br>';
					insert_one_examination_blob_without_result($link,$sid,$ex);
				}
			}
			if($exreq=='None')
			{
					if($ex==$GLOBALS['mrd'])
					{
						insert_one_examination_with_result($link,$sid,$ex,$_POST['mrd']);
					}
					elseif($ex==$GLOBALS['sample_requirement'])
					{
						//already inserted during set_sample_id()
					}
					else
					{
						if($type!='blob')
						{
							insert_one_examination_without_result($link,$sid,$ex);
						}
						else
						{
							insert_one_examination_blob_without_result($link,$sid,$ex);
						}
					}
			}
		}
	}

	return $sample_id_array	;
}

function get_one_ex_result($link,$sample_id,$examination_id)
{
		$sql='select * from result where sample_id=\''.$sample_id.'\' and examination_id=\''.$examination_id.'\'';
		//echo 'xxx'.$sql;
		$result=run_query($link,$GLOBALS['database'],$sql);
		//if(!$result){return false;}
		$ar=get_single_row($result);
		//echo  '<h4>'.$ar['result'].'</h4>';
		if(isset($ar['result']))
		{
			return $ar['result'];
		}
		else
		{
			return false;
			
		}
}

function get_one_ex_result_blob($link,$sample_id,$examination_id)
{
		$sql='select * from result_blob where sample_id=\''.$sample_id.'\' and examination_id=\''.$examination_id.'\'';
		//echo $sql;
		$result=run_query($link,$GLOBALS['database'],$sql);
		$ar=get_single_row($result);
		//echo  '<h4>'.$ar['result'].'</h4>';
		return $ar['result'];
}

function add_new_examination_and_profile($link,$sample_id,$list_of_selected_examination='',$list_of_selected_profile='')
{
	$sample_requirement=get_one_ex_result($link,$sample_id,$GLOBALS['sample_requirement']);
	$requested=array();
	$ex_requested=explode(',',$list_of_selected_examination);
	$requested=array_merge($requested,$ex_requested);
	//echo '<pre>';
	//print_r($requested);

	$profile_requested=explode(',',$list_of_selected_profile);
	//print_r($profile_requested);
	foreach($profile_requested as $value)
	{
		$psql='select * from profile where profile_id=\''.$value.'\'';
		//echo $psql;
		$result=run_query($link,$GLOBALS['database'],$psql);
		$ar=get_single_row($result);
		if(isset($ar['examination_id_list']))
		{
			$profile_ex_requested=explode(',',$ar['examination_id_list']);
		}
		else
		{
			$profile_ex_requested=array();
		}
		$requested=array_merge($requested,$profile_ex_requested);
	}
	//print_r($requested);

	$requested=array_filter(array_unique($requested));
	//print_r($requested);
	$list_of_selected_examination=$list_of_selected_examination;
	foreach ($requested as $exr)
	{
		
		$ex_data=get_one_examination_details($link,$exr);
		$edit_specification=json_decode($ex_data['edit_specification'],true);
		$type=isset($edit_specification['type'])?$edit_specification['type']:'';

		//echo '<br>'.$ex_data['sample_requirement'].'<br>';
		//echo $sample_requirement.'<br>';
		
		if($ex_data['sample_requirement']==$sample_requirement || $ex_data['sample_requirement']=='None')
		{		
		//echo '<br>'.$ex_data['sample_requirement'].'<br>';
		//echo $sample_requirement.'<br>';
		
			if($exr==$GLOBALS['mrd'])
			{
				//mrd inserted, do nothing
			}
			elseif($exr==$GLOBALS['sample_requirement'])
			{
				//already inserted
				//insert_one_examination_with_result($link,$sid,$ex,$_POST['mrd']);
			}
			elseif($type!='blob')
			{
				insert_one_examination_without_result($link,$sample_id,$exr);
			}
			else  //blob as attachment 
			{
				insert_one_examination_blob_without_result($link,$sample_id,$exr);
			}
		}
		else
		{
			
			echo '<h5>'.$ex_data['name'].' is not allowed in '.$sample_requirement.'</h5>';
		}
	}
}

function set_lable($session_name,$sample_id,$examination_details,$examination_id)
{
		echo '
			<div class="my_lable">';
			
		if($examination_details['examination_id']!=$GLOBALS['mrd'] && $examination_details['examination_id']!=$GLOBALS['sample_requirement'])
		{
		echo '
				<form method=post class="d-inline">
					<input type=hidden name=session_name value=\''.$session_name.'\'>
					<input type=hidden name=sample_id value=\''.$sample_id.'\'>
					<input type=hidden name=examination_id value=\''.$examination_id.'\'>
					
					<button type=submit  class="btn btn-danger btn-sm d-inline m-0 p-0" name=action value=delete title=Delete>X</button>	
				</form>
				';
		}		
		echo '<label for="'.$examination_details['name'].'">'.$examination_details['name'].'</label>
			</div>';
}

function set_lable_subsection($session_name,$sample_id,$examination_details,$examination_id)
{
		echo '
			<div class="my_lable">';
			
		if($examination_details['examination_id']!=$GLOBALS['mrd'] && $examination_details['examination_id']!=$GLOBALS['sample_requirement'])
		{
		echo '
				<form method=post class="d-inline">
					<input type=hidden name=session_name value=\''.$session_name.'\'>
					<input type=hidden name=sample_id value=\''.$sample_id.'\'>
					<input type=hidden name=examination_id value=\''.$examination_id.'\'>
					
					<button type=submit  class="btn btn-danger btn-sm d-inline m-0 p-0" name=action value=delete title=Delete>X</button>	
				</form>
				';
		}		
		echo '<label class="bg-warning" for="'.$examination_details['name'].'"><h3>'.$examination_details['name'].'</h3></label>
			</div>';
}

function get_new_sample_id($link,$mrd,$sample_requirement)
{
	$sample_id=find_next_sample_id($link,$sample_requirement);
	$sql='insert into result (sample_id,examination_id,result,recording_time,recorded_by)
			values (\''.$sample_id.'\', \''.$GLOBALS['mrd'].'\',\''.$mrd.'\',now(),\''.$_SESSION['login'].'\')';
	if(!run_query($link,$GLOBALS['database'],$sql))
		{echo 'Data not inserted(with)<br>'; return false;}
	else
	{
		return $sample_id;
	}
}

/*
function find_next_sample_id($link)
{
	$sqls='select ifnull(max(sample_id)+1,1) as next_sample_id from result';
	//echo $sqls;
	$results=run_query($link,$GLOBALS['database'],$sqls);
	$ars=get_single_row($results);
	return $ars['next_sample_id'];
}
*/

function find_next_sample_id($link,$sample_requirement)
{
	$sql='select * from sample_id_strategy where sample_requirement=\''.$sample_requirement.'\'';
	//echo '<h5>'.$sql.'</h5>';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$ar=get_single_row($result);
	$from=$ar['lowest_id'];
	$to=$ar['highest_id'];	

	$sqls='select ifnull(max(sample_id)+1,'.$from.') as next_sample_id from result where sample_id between '.$from.' and '.$to;
	//echo $sqls;
	$results=run_query($link,$GLOBALS['database'],$sqls);
	$ars=get_single_row($results);
	return $ars['next_sample_id'];
}

function insert_one_examination_without_result($link,$sample_id,$examination_id)
{
	$sql='insert into result (sample_id,examination_id)
			values ("'.$sample_id.'","'.$examination_id.'")';
	//echo $sql.'(without)<br>';
	if(!run_query($link,$GLOBALS['database'],$sql))
	{
		//echo $sql.'(without)<br>';
		//echo 'Data not inserted(without)<br>'; 
		return false;
	}	else{return true;}
}

function insert_one_examination_with_result($link,$sample_id,$examination_id,$result)
{
	//recording_time=now(),recorded_by=\''.$_POST['user'].'\'
				
	$sql='insert into result (sample_id,examination_id,result,recording_time,recorded_by)
			values ("'.$sample_id.'","'.$examination_id.'","'.my_safe_string($link,$result).'",now(),"'.$_SESSION['login'].'")';
	//echo $sql.'(without)<br>';
	if(!run_query($link,$GLOBALS['database'],$sql))
	{
		//echo $sql.'(without)<br>';
		//echo 'Data not inserted(with)<br>'; 
		return false;
	}	else{return true;}
}
function insert_one_examination_blob_without_result($link,$sample_id,$examination_id)
{
	$sql='insert into result_blob (sample_id,examination_id)
			values ("'.$sample_id.'","'.$examination_id.'")';
	if(!run_query($link,$GLOBALS['database'],$sql))
	{	
		//echo $sql.'(without)<br>';
		//echo 'Data not inserted(without)<br>'; 
		return false;
	}
	else{return true;}
}

function echo_export_button($sample_id_csv)
{
	echo'<form method=post id=export_button action=export.php class="d-inline-block">
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=sample_id value=\''.$sample_id_csv.'\'>
	<div class=print_hide><button type=submit class="btn btn-info  border-danger m-0 p-0" name=export>Export</button></div></form>';
}


function echo_report_export_button($sample_id_csv,$report_id)
{
	echo'<form method=post id=export_button action=export2.php class="d-inline-block">
	<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>
	<input type=hidden name=sample_id value=\''.$sample_id_csv.'\'>
	<input type=hidden name=report_id value=\''.$report_id.'\'>
	<div class=print_hide><button type=submit class="btn btn-info  border-danger m-0 p-0" name=export>Export</button></div></form>';
}

function echo_class_button($link,$class)
{
	$sql='select * from report where report_name=\''.$class.'\'';
	$result=run_query($link,$GLOBALS['database'],$sql);
	$ar=get_single_row($result);
	$ex_list=explode(',',$ar['examination_id']);
	$jarray=json_encode($ex_list);
	//echo $jarray;
	echo '<div class="d-inline-block "><div class=print_hide><button type=button class="btn btn-info d-inline-block border-danger m-0 p-0" onclick="set_print_class(\''.htmlspecialchars($jarray).'\')">'.$class.'</button></div></div>';
}



function get_search_condition($link)
{
	echo '<form method=post>';
	echo '<button type=submit class="btn btn-primary form-control" name=action value=set_search>Set Search</button>';
	echo '<div class="basic_form">';
	get_examination_data($link);
	echo '</div>';
	echo '<button type=submit class="btn btn-primary form-control" name=action value=set_search>Set Search</button>';
	echo '<input type=hidden name=session_name value=\''.session_name().'\'>';
	echo '</form>';
}

function set_search($link,$action='')
{
	$ex_requested=explode(',',$_POST['list_of_selected_examination']);
	//print_r($ex_requested);
	echo '<form method=post '.$action.'>';
		foreach($ex_requested as $v)
		{
			$examination_details=get_one_examination_details($link,$v);
			echo '<div class="basic_form">';
			echo '	<label class="my_label" for="'.$examination_details['name'].'">'.$examination_details['name'].'</label>
					<input 
						id="'.$examination_details['name'].'" 
						name="'.$examination_details['examination_id'].'" 
						data-exid="'.$examination_details['examination_id'].'" 
						class="form-control" >
					<p class="help">Enter details for search</p>';
			echo '</div>';
		}
	echo '<button type=submit class="btn btn-primary form-control" name=action value=search>Search</button>';
	echo '<input type=hidden name=session_name value=\''.session_name().'\'>';
	echo '</form>';
}

function prepare_search_array($link)
{
	$ret=array();
	foreach($_POST as $k=>$v)
	{
		if(is_int($k) && strlen($v)>0)
		{
			$ret[$k]=$v;
		}
	}	
	return $ret;
}

function get_sample_with_condition($link,$exid,$ex_result,$sid_array=array(),$first=FALSE)
{
	$ret=array();
	
	if($first===TRUE)
	{
		$sql='select sample_id from result 
				where 
					examination_id=\''.$exid.'\' and 
					result like \'%'.$ex_result.'%\' limit 50';
		//echo $sql.'<br>';
		$result=run_query($link,$GLOBALS['database'],$sql);
		while($ar=get_single_row($result))
		{
			$ret[]=$ar['sample_id'];
		}
		return $ret;
	}
	
	//else do as follows
	foreach($sid_array as $v)
	{
		$sql='select sample_id from result 
				where 
					examination_id=\''.$exid.'\' and 
					result like \'%'.$ex_result.'%\' and
					sample_id=\''.$v.'\' limit 50';
		//echo $sql.'<br>';
		$result=run_query($link,$GLOBALS['database'],$sql);
		if(get_row_count($result)>0)
		{
			$ret[]=$v;
		}
	}
	return $ret;
}


function set_sample_id($link, $sample_required_array)
{
	//print_r($sample_required_array);
	$sample_id_array=array();
	foreach ($sample_required_array as $stype)
	{
		if($stype!='None')
		{
			$sample_id_array[$stype]=find_next_sample_id($link,$stype);
			//we must REALLY insert something in result to make increment possible in next cycle
			//otherwise sample id for given stype will be returned
			//so insert sample_requirement as first result!!!
			//1000 is sample_requirement
			//echo 'pp';
			//echo $GLOBALS['sample_requirement'];
			insert_one_examination_with_result($link,$sample_id_array[$stype],$GLOBALS['sample_requirement'],$stype);
			//echo 'qq';
		}
	}
	return $sample_id_array;
}


////////////// TCPDF Functions///////////////////////

function print_sample($link,$sample_id,$pdf)
{
	     //$pdf = new ACCOUNT1('P', 'mm', 'A4', true, 'UTF-8', false);
	$pdf->startPageGroup();
     
	     $pdf->sample_id=$sample_id;
	     $pdf->link=$link;
	     $pdf->profile_wise_ex_list=get_profile_wise_ex_list($link,$sample_id);
	     if($pdf->profile_wise_ex_list===false){return;}

	ob_start();
		view_sample_p($link,$sample_id,$pdf->profile_wise_ex_list);
		$myStr = ob_get_contents();
	ob_end_clean();

	//echo $myStr;
	//exit(0);
	     //left,top,right
	     $pdf->SetMargins(10, 40, 10);
	     $pdf->SetAutoPageBreak(TRUE, 30);
	     
	     $pdf->SetFont('courier', '', 9);
	     //$pdf->SetMargins(10, $pdf->current_y, 10); //no effect, page not added
	     //$pdf->SetY($pdf->current_y); //no effect, page not added
		 $pdf->AddPage();
		 $pdf->SetY($pdf->current_y); //required , setMargin after add page have no effect
		 $pdf->SetMargins(10, $pdf->current_y, 10); //will take effect from next page onwards

	     $pdf->writeHTML($myStr, true, false, true, false, '');
	     
	     //$pdf->writeHTML(count($GLOBALS['img_list']), true, false, true, false, '');
	 
	     //prepare for graphics
	    //$y=$pdf->GetY(); //Y first?
		//$x=$pdf->GetX();
		
		//$i=0;
			
	     //foreach($GLOBALS['img_list'] as $k=>$v)
	     //{
			////somehow manual calculation of X and Y is required
			////public function Image($file, $x='', $y='', $w=0, $h=0, $type='', $link='', $align='', $resize=false, 
			////$dpi=300, $palign='', $ismask=false, $imgmask=false, $border=0, $fitbox=false, $hidden=false, $fitonpage=false, $alt=false, $altimgs=array()) {
			//$pdf->Image('@'.$v,$x+$i*40,$y+$i*0,40,20,$type='', $link='', $align='', $resize=true,
						//$dpi=300, $palign='', $ismask=false, $imgmask=false, $border=1);
			//$i++;
		 //}
				     
	     //$pdf->Output('report-'.$sample_id.'.pdf', 'I');
}

function display_dw_png($ex_result,$label)
{
	$ar=str_split($ex_result);
	
	$width=256; //128 X 2
    $height=128; //256;//223+32=255 make is half to save space
    $im = imagecreatetruecolor($width,$height);
    $white = imagecolorallocate($im, 255, 255, 225);
    $black = imagecolorallocate($im, 0,0,0);
	imagefill($im,0,0,$white);
	imagestring($im, 5, 3, 1, $label, $black);

	$px=0;
	$py=256;
	$y=2;
	foreach ($ar as $k=>$v)
	{
		$y=(256-ord($v))/2 +16; //make half add 16 to get baseline
		$x=$k*2;	//every two pixel
		imageline ( $im , $px , $py , $x , $y , $black ) ;
		
		$py=$y;
		$px=$x;
	}
	
	ob_start();	
	imagepng($im);
	$myStr = ob_get_contents();
	ob_end_clean();
	imagedestroy($im);	
	return $myStr;
}



function display_png($ex_result,$label='',$width=0,$height=0)
{	
	$encoded_image=base64_encode($ex_result);	
	echo '<img src="data:image/png;base64,'.$encoded_image.'" />';
}


function display_png_p($ex_result,$label='',$width=100,$height=100)
{	
	$encoded_image=base64_encode($ex_result);	
	//Ha Ha!!! lots of time wasted for silly things.Thanks to internet
	//$final='data:image/png;base64,@'.$encoded_image;
	//$img = '<img src="@' . preg_replace('#^data:image/[^;]+;base64,#', '', $final) . ' " width="'.$width.'" height="'.$height.'"/> ';
	//$img = '<img src="@' . preg_replace('#^data:image/[^;]+;base64,#', '', $final) . ' " width="'.$width.'" height="'.$height.'"/> ';
	
	//$img = '<img src="@'.$encoded_image.'" width="'.$width.'" height="'.$height.'"/> ';
	$img = '<img src="@'.$encoded_image.'" width="'.$width.'" /> ';
	echo $img;
}

function view_sample_p($link,$sample_id,$profile_wise_ex_list)
{
	$ex_list=get_result_of_sample_in_array($link,$sample_id);
	echo '<table border="0"  cellpadding="2">';

	foreach($profile_wise_ex_list as $kp=>$vp)
	{
		if($kp==$GLOBALS['pid_profile']){continue;}	//pid is displyed on each page//not needed here

		$pinfo=get_profile_info($link,$kp);
		$profile_edit_specification=json_decode($pinfo['edit_specification'],true);
		$print_hide=isset($profile_edit_specification['print_hide'])?$profile_edit_specification['print_hide']:'';
		$print_style=isset($profile_edit_specification['print_style'])?$profile_edit_specification['print_style']:'';
		
		if($print_hide=='yes'){continue;}	//not to be printed
		
		$display_name=isset($profile_edit_specification['display_name'])?$profile_edit_specification['display_name']:'';

		if($display_name!='no')
		{		
			echo '<tr><th colspan="3"><h2><u>'.$pinfo['name'].'</u></h2></th></tr>';
		}
		
		//if($pinfo['profile_id']>$GLOBALS['max_non_ex_profile'])

		if($print_style=='horizontal')
		{	
			$count=1;

			foreach($vp as $ex_id)
			{
				if($count%3==1)
				{
					echo '<tr>';
				}

				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';					
				if($type!='blob')
				{
					echo '<td style="border-right:0.1px solid black;">';
					view_field_hr_p($link,$ex_id,$ex_list[$ex_id]);	
					echo '</td>';
				}
				else
				{
					//view_field_blob_hr($link,$ex_id,$sample_id);	
				}
				
				
				if($count%3==0)
				{
					echo '</tr>';
				}
			$count++;
			}
			$count--;
			
			if($count%3==1){echo '<td></td><td></td></tr>';}
			if($count%3==2){echo '<td></td></tr>';}
		}
		elseif($print_style=='vertical')
		{	
			foreach($vp as $ex_id)
			{
				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';					
				if($type!='blob')
				{
					view_field_vr_p($link,$ex_id,$ex_list[$ex_id]);	
				}
				else
				{
					view_field_blob_vr_p($link,$ex_id,$sample_id);	
				}
			}
		}
		else
		{
		
			$header=isset($profile_edit_specification['header'])?$profile_edit_specification['header']:'';
			if($header!='no')
			{
				echo_result_header_p();
			}
		
			foreach($vp as $ex_id)
			{

				$examination_details=get_one_examination_details($link,$ex_id);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';
								
				if($type!='blob')
				{
					view_field_p($link,$ex_id,$ex_list[$ex_id]);	
				}
				else
				{
					
				}
			}
		}				
	}
	
	echo '</table>';	
}

function view_field_p($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$type=isset($edit_specification['type'])?$edit_specification['type']:'';

		$interval_l=isset($edit_specification['interval_l'])?$edit_specification['interval_l']:'';
		$cinterval_l=isset($edit_specification['cinterval_l'])?$edit_specification['cinterval_l']:'';
		$ainterval_l=isset($edit_specification['ainterval_l'])?$edit_specification['ainterval_l']:'';
		$interval_h=isset($edit_specification['interval_h'])?$edit_specification['interval_h']:'';
		$cinterval_h=isset($edit_specification['cinterval_h'])?$edit_specification['cinterval_h']:'';
		$ainterval_h=isset($edit_specification['ainterval_h'])?$edit_specification['ainterval_h']:'';
		$img=isset($edit_specification['img'])?$edit_specification['img']:'';

		if($img=='dw')
		{
			//echo '<tr>';
			//echo '<td style="border: 0.3px solid black;">'.$examination_details['name'].'</td>';
			//echo '<td style="border: 0.3px solid black;">';
			
			//just save graphics in global array, for display leter on
			//echo 'sssss';
			$GLOBALS['img_list'][$examination_details['name']]=display_dw_png($ex_result,$examination_details['name']);
			//echo '</td>';
			//echo '<td style="border: 0.3px solid black;"></td></tr>';			
		}
		elseif($type=='subsection')
		{		
				echo '<tr>';
				echo '	<td style="border: 0.3px solid black;"></td>
				<td style="border: 0.3px solid black;"><h3 align="center">'.$examination_details['name'].'</h3></td>
				<td style="border: 0.3px solid black;"></td>';
				echo '</tr>';
		//echo '	<pre><table border="1"><tr><td>sadda</td><td>sadda</td></tr><tr><td>sadda</td><td>sadda</td></tr></table>'.htmlspecialchars($help).'</pre>';
		}
		else
		{		
				echo '<tr>';
		echo '	<td style="border: 0.3px solid black;">'.$examination_details['name'].'</td>
				<td style="border: 0.3px solid black;"><pre>'.htmlspecialchars($ex_result.' '.
				decide_alert($ex_result,$interval_l,$cinterval_l,$ainterval_l,$interval_h,$cinterval_h,$ainterval_h)).'</pre></td>
				<td style="border: 0.3px solid black;">'.nl2br(htmlspecialchars($help)).'</td>';
				echo '</tr>';
		//echo '	<pre><table border="1"><tr><td>sadda</td><td>sadda</td></tr><tr><td>sadda</td><td>sadda</td></tr></table>'.htmlspecialchars($help).'</pre>';
		}

}		

function display_dw_p($ex_result)
{
	$ar=str_split($ex_result);

	$width=256; //128 X 2
    $height=128; //256;//223+32=255 make is half to save space
    $im = imagecreatetruecolor($width,$height);
    $white = imagecolorallocate($im, 255, 255, 225);
    $black = imagecolorallocate($im, 0,0,0);
	imagefill($im,0,0,$white);
	$px=0;
	$py=256;
	foreach ($ar as $k=>$v)
	{
		$y=(256-ord($v))/2 +16; //make half add 16 to get baseline
		$x=$k*2;	//every two pixel
		imageline ( $im , $px , $py , $x , $y , $black ) ;
		$py=$y;
		$px=$x;
	}
	
	ob_start();	
	imagepng($im);
	$myStr = base64_encode(ob_get_contents());
	ob_end_clean();

	//echo "<img src='data:image/png;base64,".$myStr."'/>";
	echo '<img src=\'data:image/png;base64,'.$myStr.'\'>';
	//echo "x<img src='img/img.png'>y";
	imagedestroy($im);	
}

function view_field_hr_p($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$interval=isset($edit_specification['interval'])?$edit_specification['interval']:'';
		
		echo '<b>'.$examination_details['name'].':</b> '.htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''));
}	


function view_field_vr_p($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		//$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$interval=isset($edit_specification['interval'])?$edit_specification['interval']:'';
		$type=isset($edit_specification['type'])?$edit_specification['type']:'';
		
		if($type=='subsection')
		{
			echo '	<tr>
					<td colspan="3"><h2 style="text-align:center">'.$examination_details['name'].'</h2></td>
				</tr>'	;
		}
		else
		{

				$formatted=nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','','')));
				$bold_formatted1=str_replace('(((','<b>',$formatted);
				$bold_formatted2=str_replace(')))','</b>',$bold_formatted1);
							
			if(strlen($ex_result)<$GLOBALS['print_side_or_below'])
			{
				echo '	<tr>
					<td colspan="3"><b style="font-size: 1.1em;">'.$examination_details['name'].':</b>'.$bold_formatted2.'</td>
				</tr>';
			}
			else
			{
				//$formatted=nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','','')));
				//$bold_formatted1=str_replace('(((','<b>',$formatted);
				//$bold_formatted2=str_replace(')))','</b>',$bold_formatted1);
				//$formatted=nl2br($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''));
				echo '	<tr>
					<td colspan="3"><h3>'.$examination_details['name'].'</h3></td><td></td><td></td>
				</tr>
				<tr>
					<td colspan="3">'.$bold_formatted2.'</td>
					
				</tr>';
			}
		}		
}	

//<td colspan="3"><pre>'.nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''))).'</pre></td>
//<td colspan="3">'.nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''))).'</td>
//<td colspan="3">'.nl2br($ex_result.' '.decide_alert($ex_result,$interval,'','','','','')).'</td>

function view_field_vr($link,$ex_id,$ex_result)
{
		$examination_details=get_one_examination_details($link,$ex_id);
		$edit_specification=json_decode($examination_details['edit_specification'],true);
		//$help=isset($edit_specification['help'])?$edit_specification['help']:'';
		$interval=isset($edit_specification['interval'])?$edit_specification['interval']:'';
		$type=isset($edit_specification['type'])?$edit_specification['type']:'';
		
		if($type=='subsection')
		{
			echo '	<div>
					<h2 style="text-align:center">'.$examination_details['name'].'</h2>
				</div>'	;
		}
		else
		{
			if(strlen($ex_result)<$GLOBALS['print_side_or_below'])
			{
				echo '	<div>
					<b>'.$examination_details['name'].':</b>'.htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','','')).'
				</div>';
			}
			else
			{
				echo '	<div>
					<h4>'.$examination_details['name'].'</h4>
				</div>
				<div>
					'.nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''))).'
				</div>';
			}
		}		
}	
//'.nl2br(htmlspecialchars($ex_result.' '.decide_alert($ex_result,$interval,'','','','',''))).'
//'.nl2br($ex_result.' '.decide_alert($ex_result,$interval,'','','','','')).'

function echo_result_header_p()
{
	echo '<tr><td width="25%">Examination</td><td width="30%">Result</td><td width="45%">Unit, Ref. Intervals ,(Method)</td></tr>';
}

function get_profile_wise_ex_list($link,$sample_id)
{
	$ex_list=get_result_of_sample_in_array($link,$sample_id);
	//print_r($ex_list);
	$rblob=get_result_blob_of_sample_in_array($link,$sample_id);
	//print_r($rblob);
	$result_plus_blob_requested=$ex_list+$rblob;
	//print_r($result_plus_blob_requested);
	if(count($result_plus_blob_requested)==0)
	{
		echo '<h3>Nothing requested for sample_id='.$sample_id.'</h3>';
		return false;
	}
	
	return $profile_wise_ex_list=ex_to_profile($link,$result_plus_blob_requested);
}

function dashboard($link)
{
	$sql='select * from dashboard order by priority desc';
	echo '<h3>Dashboard</h3>';
	$result=run_query($link,$GLOBALS['database'],$sql);
	
	echo '<ul>';
	while($ar=get_single_row($result))
	{
		echo '<li><pre>';
		echo '<span class="badge badge-primary ">'.$ar['topic'].'</span><p class="text-dark">'.$ar['description'].'</p>';
		echo '</pre></li>';
	}
	echo '</ul>';
		
}


class ACCOUNT1 extends TCPDF {
	public $sample_id;
	public $link;
	public $current_y;
	public $profile_wise_ex_list;
	public function Header() 
	{
		ob_start();	
	$sr=get_one_ex_result($this->link,$this->sample_id,$GLOBALS['sample_requirement']);
	$sr_array=explode('-',$sr);
	$header=$GLOBALS[$sr_array[2]];
	
	echo '<table  cellpadding="2">
	<tr><td style="text-align:center" colspan="3"><h2>'.$header['name'].'</h2></td></tr>
	<tr><td style="text-align:center" colspan="3"><h3>'.$header['section'].'<b> (Sample ID:</b> '.$this->sample_id.')</h3></td></tr>
	<tr><td style="text-align:center" colspan="3"><h5>'.$header['address'].'</h5></td></tr>
	<tr><td style="text-align:center" colspan="3"><h5>'.$header['phone'].'</h5></td></tr>';

			$count=1;
			foreach($this->profile_wise_ex_list[$GLOBALS['pid_profile']] as $v)
			{
				
				if($count%3==1)
				{
					echo '<tr>';
				}

				
				$examination_details=get_one_examination_details($this->link,$v);
				$edit_specification=json_decode($examination_details['edit_specification'],true);
				$type=isset($edit_specification['type'])?$edit_specification['type']:'';

				if($type!='blob')
				{
					$r=get_one_ex_result($this->link,$this->sample_id,$v);
					echo '<td style="border-right:0.1px solid black;">';
					view_field_hr_p($this->link,$v,$r);	
					echo '</td>';
				}
				else
				{
					//view_field_blob_hr($link,$ex_id,$sample_id);	
				}
				
				
				if($count%3==0)
				{
					echo '</tr>';
				}
			$count++;
			}
			$count--;
			
			if($count%3==1){echo '<td></td><td></td></tr>';}
			if($count%3==2){echo '<td></td></tr>';}
			
	echo '</table>
	<hr></hr>';

	 $myStr = ob_get_contents();
	 ob_end_clean();
	$this->SetY(10);
	$this->writeHTML($myStr, true, false, true, false, '');
	$this->current_y=$this->GetY();
	}
	
	public function Footer() 
	{
	    $this->SetY(-20);
		//$this->Cell(0, 10, 'Page '.$this->getAliasNumPage().'/'.$this->getAliasNbPages(), 0, false, 'C', 0, '', 0, false, 'T', 'M');
		$this->Cell(0, 10, 'Page '.$this->getPageNumGroupAlias().'/'.$this->getPageGroupAlias(), 0, false, 'C', 0, '', 0, false, 'T', 'M');
	}	
}

///////////dashbard functions/////

function show_dashboard($link)
{
	get_sql($link);
	
}

function get_sql($link)
{
        if(!$result=run_query($link,$GLOBALS['database'],'select * from view_info_data')){return false;}

        echo '
        <table border=1 class="table-striped table-hover"><tr><th colspan=20>Select the data to view</th></tr>';

        $first_data='yes';

        while($array=get_single_row($result))
        {
                if($first_data=='yes')
                {
                        echo '<tr>';
                        foreach($array as $key=>$value)
                        {
							    if($key!='sql'){
                                echo '<th bgcolor=lightgreen>'.$key.'</th>';}
                        }
                        echo '</tr>';
                        $first_data='no';
                }

				echo'<form style="margin-bottom:0;" method=post>';
                echo '<tr>';
                foreach($array as $key=>$value)
                {
					echo'<input type=hidden name=session_name value=\''.$_SESSION['login'].'\'>';
					echo '<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>';
                       if($key=='id')
                        { 
                         echo '<td>
							<input type=hidden name=action value=display_data>
							<button class="btn btn-danger" type=submit name=id value=\''.$value.'\'>'.$value.'</button></td>';
                        }
                        elseif($key=='sql'){}
                        elseif($key=='Fields')
                        {
                                echo '<td class="badge badge-warning">'.$value.'</td>';							
						}
                        else
                        {
                                echo '<td>'.$value.'</td>';
                        }
                }
				echo '</tr>';
				echo '</form>';

        }
        echo '</table>';
    
}
function prepare_result_from_view_data_id($link,$id)
{

         if(!$result_id=run_query($link,$GLOBALS['database'],'select * from view_info_data where id=\''.$id.'\''))
         {
			 echo '<h1>Problem</h1>';
		 }
		 else
		 {
			 echo '<h1>Success</h1>';
		 }
        $array_id=get_single_row($result_id);

        $sql=$array_id['sql'].'';
        $info=$array_id['info'];

		//echo $sql.'<br>';
        ////modify sql
        //print_r($_POST);
        
        if(isset($_POST['__p1'])) 
        {
			if(strlen($_POST['__p1'])>0)
			{
				$sql=str_replace('__p1',$_POST['__p1'],$sql);			
				$p1=$_POST['__p1'];
			}
			else
			{
				$p1='';
			}
		}
		else
		{
			$p1='';
		}


        if(isset($_POST['__p2'])) 
        {
			if(strlen($_POST['__p2'])>0)
			{
				$sql=str_replace('__p2',$_POST['__p2'],$sql);			
				$p2=$_POST['__p2'];
			}
			else
			{
				$p2='';
			}
		}
		else
		{
			$p2='';
		}

        if(isset($_POST['__p3'])) 
        {
			if(strlen($_POST['__p3'])>0)
			{
				$sql=str_replace('__p3',$_POST['__p3'],$sql);			
				$p3=$_POST['__p3'];
			}
			else
			{
				$p3='';
			}
		}
		else
		{
			$p3='';
		}

        if(isset($_POST['__p4'])) 
        {
			if(strlen($_POST['__p4'])>0)
			{
				$sql=str_replace('__p4',$_POST['__p4'],$sql);			
				$p4=$_POST['__p4'];
			}
			else
			{
				$p4='';
			}
		}
		else
		{
			$p4='';
		}
        //////////////
		//echo $sql;


        if(!$result=run_query($link,$GLOBALS['database'],$sql))
        {
			 echo '<h1>Problem</h1>';
		}
		 else
		 {
			 //echo '<h1>Success</h1>';
		 }


		echo_export_button_dashboard($link,$id,$p1,$p2,$p3,$p4);
		display_sql_result_data($result);

}


function echo_export_button_dashboard($link,$id,$p1,$p2,$p3,$p4)
{
	echo '<form method=post class="d-inline" action=export3.php>';
		echo '<input type=hidden name=session_name value=\''.$_SESSION['login'].'\'>';
		echo '<input type=hidden name=session_name value=\''.$_POST['session_name'].'\'>';			
		echo '<input type=hidden name=id value=\''.$id.'\'>';
		echo '<input type=hidden name=__p1 value=\''.$p1.'\'>		
			<input type=hidden name=__p2 value=\''.$p2.'\'>		
			<input type=hidden name=__p3 value=\''.$p3.'\'>		
			<input type=hidden name=__p4 value=\''.$p4.'\'>		
			
			<button class="btn btn-info"  
			formtarget=_blank
			type=submit
			name=action
			value=export>Export</button>
		</form>';
}
	
function display_sql_result_data($result)
{
	echo '<button data-toggle="collapse" data-target="#sql_result" class="btn btn-dark">Show/Hide Result</button>';
	echo '<div id="sql_result" class="collapse show">';		
		
	
       echo '<table border=1 class="table-striped table-hover">';
				
        $first_data='yes';

        while($array=get_single_row($result))
        {
			//echo '<pre>';
			//print_r($array);
                if($first_data=='yes')
                {
                        echo '<tr bgcolor=lightgreen>';
                        foreach($array as $key=>$value)
                        {
                                echo '<th>'.$key.'</th>';
                        }
                        echo '</tr>';
                        $first_data='no';
                }
                echo '<tr>';
                foreach($array as $key=>$value)
                {
                        echo '<td>'.$value.'</td>';
                }
                echo '</tr>';

        }
        echo '</table>';	
	echo '</div>';	
	
}
//111119500892
//one

function prepare_result_for_export($link,$id)
{

         if(!$result_id=run_query($link,$GLOBALS['database'],'select * from view_info_data where id=\''.$id.'\''))
         {
			 //echo '<h1>Problem</h1>';
		 }
		 else
		 {
			// echo '<h1>Success</h1>';
		 }
        $array_id=get_single_row($result_id);

        $sql=$array_id['sql'].'';
        $info=$array_id['info'];

		//echo $sql.'<br>';
        ////modify sql
        //print_r($_POST);
        
        if(isset($_POST['__p1'])) 
        {
			if(strlen($_POST['__p1'])>0)
			{
				$sql=str_replace('__p1',$_POST['__p1'],$sql);			
				$p1=$_POST['__p1'];
			}
			else
			{
				$p1='';
			}
		}
		else
		{
			$p1='';
		}


        if(isset($_POST['__p2'])) 
        {
			if(strlen($_POST['__p2'])>0)
			{
				$sql=str_replace('__p2',$_POST['__p2'],$sql);			
				$p2=$_POST['__p2'];
			}
			else
			{
				$p2='';
			}
		}
		else
		{
			$p2='';
		}

        if(isset($_POST['__p3'])) 
        {
			if(strlen($_POST['__p3'])>0)
			{
				$sql=str_replace('__p3',$_POST['__p3'],$sql);			
				$p3=$_POST['__p3'];
			}
			else
			{
				$p3='';
			}
		}
		else
		{
			$p3='';
		}

        if(isset($_POST['__p4'])) 
        {
			if(strlen($_POST['__p4'])>0)
			{
				$sql=str_replace('__p4',$_POST['__p4'],$sql);			
				$p4=$_POST['__p4'];
			}
			else
			{
				$p4='';
			}
		}
		else
		{
			$p4='';
		}
        //////////////
		//echo $sql;


        if(!$result=run_query($link,$GLOBALS['database'],$sql))
        {
			 echo '<h1>Problem</h1>';
		}
		 else
		 {
			 echo '<h1>Success</h1>';
		 }


		export_data($result);
}

function export_data($result)
{
	    $fp = fopen('php://output', 'w');
	    if ($fp && $result) 
	    {
		    header('Content-Type: text/csv');
		    header('Content-Disposition: attachment; filename="export.csv"');
		
	    	$first='yes';
		
		   while ($row = get_single_row($result))
		   {
			    if($first=='yes')
			    {
				  fputcsv($fp, array_keys($row));
				  $first='no';
			    }
			
			fputcsv($fp, array_values($row));
		  }
	   }
}

function show_examination_bin()
{
	echo 
	'<div class="position-fixed bg-secondary">
		<button 
		type=button
		class="btn btn-warning btn-sm p-0 m-0 d-inline"
		 data-toggle="collapse" 
		data-target="#advice" href="#advice"><img src="img/copypaste.png" width=20></button>
		<div class="p-3 collapse" id="advice">';
		echo '<p id=cb_4 onclick="clear_bin()" class="bg-danger d-inline">clear</p>
			<p id=cb_5 onclick="copy_binn()" class="bg-warning d-inline">copy</p>';
		copy_bin_text($link);	
			echo '<textarea id=cb_ta cols=50 rows=4></textarea>';
		echo '</div>
	</div>';
}
//////////end of dashboard functions

?>
