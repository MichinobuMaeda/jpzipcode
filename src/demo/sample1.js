/**
 * Copyright 2012 Michinobu Maeda.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *	 http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var prevzip = ''
var addrlist = null

/** 初期処理 */
function s1Init() {
  s1GetJaonData('pref', s1InitPrefList);
  document.getElementById("s1zip").focus();
  document.getElementById("s1duparea").style.visibility = "hidden";
}

/** pref.json のデータを基に都道府県一覧のリストを作成する。 */
function s1InitPrefList(data) {
  pref = document.getElementById("s1pref");
  pref.innerHTML = '';
  for (code in data) {
    pref.innerHTML += '<option value="' + code.replace(/\D/g, '') + '">' + data[code] + '</option>';
  }
}

/** 郵便番号に対応するデータを取得する。 */
function s1GetAddress() {
  zip = document.getElementById("s1zip").value;
  if (zip.length < 7) { return; }
  if (prevzip == zip) { return; }
  prevzip = zip;
  document.getElementById("s1city").focus();
  s1GetJaonData(zip.substr(0, 3) + '/' + zip.substr(3, 2), s1SetAddress);
}

/** 郵便番号に対応するデータを設定する。 */
function s1SetAddress(data) {
  if (data == null) {
    document.getElementById("s1zip").focus();
    window.alert(prevzip + " に該当するデータがありません。");
    return;
  }
  count = 0;
  index = 0;
  for (i = 0; i < data.length; ++i) {
    if (data[i]['z'] == zip) {
      ++ count;
      index = i;
    }
  }
  if (count == 0) {
    document.getElementById("s1zip").focus();
    window.alert(prevzip + " に該当するデータがありません。")
  } else if (count == 1) {
    document.getElementById("s1duparea").style.visibility = "hidden";
    addrlist = data
    s1SetData(index);
  } else {
    addrlist = data
    list = document.getElementById("s1dup");
    list.innerHTML = '<option value="-" selected>-- 選択してください。 --</option>';
    for (i = 0; i < data.length; ++i) {
      if (data[i]['z'] == zip) {
        addr = ''
        if (data[i]['pn']) { addr += data[i]['pn']; }
        if (data[i]['cn']) { addr += data[i]['cn']; }
        if (data[i]['s'])  { addr += data[i]['s']; }
        if (data[i]['n'])  { addr += data[i]['n']; }
        if (data[i]['b'])  { addr += data[i]['b']; }
        if (data[i]['f'])  { addr += data[i]['f']; }
        if (data[i]['j'])  { addr += data[i]['j']; }
        if (data[i]['r'])  { addr += " ※" + data[i]['r']; }
        if (addr.length > 32) { addr =  addr.substr(0, 30) + ".."; }
        list.innerHTML += '<option value="' + i + '">' + addr + '</option>';
      }
    }
    document.getElementById("s1duparea").style.visibility = "visible";
    document.getElementById("s1dup").focus();
  }
}

/** 各項目の値を設定する。*/
function s1SetData(index) {
  data = addrlist[index];
  document.getElementById("s1pref").value = '';
  document.getElementById("s1city").value = '';
  document.getElementById("s1add1").value = '';
  document.getElementById("s1add2").value = '';
  document.getElementById("s1bldg").value = '';
  document.getElementById("s1note").value = '';
  if (data['pc']) {
    document.getElementById("s1pref").value = data['pc'];
  }
  if (data['cn']) {
    document.getElementById("s1city").value = data['cn'];
  }
  if (data['s']) {
    document.getElementById("s1add1").value = data['s'];
  }
  if (data['n']) {
    document.getElementById("s1add2").value = data['n'];
  }
  if (data['b']) {
    document.getElementById("s1add2").value += data['b'];
  }
  if (data['f']) {
    document.getElementById("s1add2").value += data['f'];
  }
  if (data['j']) {
    document.getElementById("s1bldg").value = data['j'];
  }
  if (data['r']) {
    document.getElementById("s1note").value = data['r'];
  }
}

/** 選択結果を設定する。 */
function s1SetSelectedData() {
  index = document.getElementById("s1dup").value;
  if (index == "-") { return; }
  document.getElementById("s1city").focus();
  s1SetData(index);
}

/** jsonデータを取得する。 */
function s1GetJaonData(id, handler) {
  var xmlhttp = window.XMLHttpRequest
      ? new XMLHttpRequest()
      : new ActiveXObject("Microsoft.XMLHTTP");
  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState != 4) { return; }
    if (xmlhttp.status != 200) {
      handler(null);
    } else {
      handler(eval('(' + xmlhttp.responseText + ')'));
    }
  };
  xmlhttp.open('GET', '/data/trg/z/' + id + '.json', true);
  xmlhttp.send();
}
