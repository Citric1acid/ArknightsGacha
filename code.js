/* 明日方舟模拟寻访系统
html页面引用的js
*/
const STAR = "★";
const CAREERS = ["先锋", "狙击", "近卫", "术师", "重装", "医疗", "特种", "辅助"];

function Random_number(n) {
	// return a random integer in 0 ~ n-1
	return Math.floor(Math.random() * n)
}

function Random_choice(arr) {
	// return a random item in arr
	return arr[Random_number(arr.length)]
}

function all_of(obj) {
	// return an array containing all arrays in obj
	var result = [];
	for (i in obj) {
		if (typeof obj[i] == "object" && Array.isArray(obj[i])) {
			result = result.concat(obj[i]);
		}
	}
	return result
}

function show_all_names(arr) {
	var result = "";
	for (let i in arr) {
		if (i != 0) {
			result += " / ";
		}
		result += arr[i].name;
	}
	return result
}

/*function Unique(arr) {
	var result = [];
	for (i in arr) {
		if (! result.find((item) => item == arr[i])) {
			result.push(arr[i]);
		}
	}
	return result
}*/

function Star(p) {
	// 选择星数
	// p: probabilities of 3~6 stars
	var x = Math.random();
	if (x < p[0]) { return 3 }
	else if (x < p[0] + p[1]) { return 4 }
	else if (x < p[0] + p[1] + p[2]) { return 5 }
	else { return 6 }
}

function Show_star(star) {
	// 显示星数
	var show_stars = "";
	for (let i = 0; i < star; i += 1) {
		show_stars += STAR;
	}
	return show_stars
}

function Select(star) {
	// 选择稀有度为star的干员
	var choices;
	// 用0~1的随机数决定是否抽到up
	var x = Math.random();
	if (x < operator_in_banner.prob[star]) {
		// 抽到up
		choices = operator_in_banner.prob_up[star];
	} else {
		// 未抽到up
		choices = operator_in_banner.common[star].slice();
		// 添加5倍提升up
		if (star == 6 && operator_in_banner.prob[0] == "*5") {
			for (let i = 0; i < 5; i += 1) {
				choices = choices.concat(operator_in_banner.prob_up[0]);
			}	
		}
	}
	return Random_choice(choices)
}

function Gacha() {
	// 寻访一次
	num_get += 1;

	if (get_five_star == 1) {
		// 五星保底
		p = [0, 0, 0.98, 0.02];
	} else {
		p = p_defalt.slice();  //reset p
	}
	if (no_six_star > 50) {
		// 六星保底
		var p6 = 0.02 * (no_six_star - 49);
		p[3] = p6;
		p[0] = (1 - p6) / 0.98 * 0.4;
		p[1] = (1 - p6) / 0.98 * 0.5;
		p[2] = (1 - p6) / 0.98 * 0.08;
	}
	
	// determine the star first
	var star = Star(p);
	console.log("star: " + star);
	if (star < 5 && get_five_star > 0) {
		get_five_star -= 1;
	} else {
		get_five_star = 0;
	}
	if (star != 6) {
		no_six_star += 1;
	} else {
		no_six_star = 0;
		p = p_defalt.slice(); // reset p
	}

	// then select an operator 
	var result = Select(star);
	console.log("operator: " + result.name);

	// 添加到已有干员
	let i;
	if ((i = own.findIndex((item) => item.name == result.name)) >= 0) {
		own[i].count += 1;
	} else {
		own.push({"name": result.name, count: 1});
	}

	return result
}

function Select_banner(n = 0) {
	if (lock) return; // 锁住时无法切换卡池

	// 选择第n个卡池
	var banner = banners[n];
	var banner_up = banner.prob_up; // 所有up的干员
	// 加载保存的数据
	banner_data = load_banner_data();
	var data = banner_data[banner.banner_name] || {"get_five_star": 10, "num_get": 0, "no_six_star": 0, "p": p_defalt.slice()};
	// 保存原卡池信息
	store_banner_data(operator_in_banner.banner_name);

	// 显示卡池名称
	$("#dropdownMenuButton").html(banner.banner_name);
	// 重置五星保底
	get_five_star = data.get_five_star;
	if (get_five_star > 0) {
		$("#num5 span").html(get_five_star);
		$("#num5").show();
	} else {
		$("#num5").hide();
	}
	// 重置六星保底
	if (banner.limited) {
		no_six_star = data.no_six_star;
		p = data.p;
		$("#banner-type").html("此卡池为限定寻访");
		$("#banner-type").css("color", "orchid");
	} else {
		// 还原常规池次数
		no_six_star = banner_data["_common"].no_six_star;
		p = banner_data["_common"].p;
		$("#banner-type").html("此卡池为标准寻访");
		$("#banner-type").css("color", "deepskyblue");
	}
	num_get = data.num_get;
	$("#num6").html(no_six_star);
	$("#prob6").html(p[3] * 100);
	$("#num-get").html(num_get);
	$("#get1").hide();
	$("#get10").hide();

	// 读取干员信息
	// reset
	operator_in_banner = {"banner_name": banner.banner_name,
		"limited": banner.limited,
		"common": [0, 0, 0, [], [], [], []], // 3星~6星, 前面留空
		"prob_up": [[], 0, 0, [], [], [], []], // 3星~6星, [0]放5倍提升
		"prob": [0, 0, 0, 0, 0, 0, 0]
	};
	for (let o of operators) {
		// up干员
		let up;
		if (up = banner_up.find((item) => item.name == o.name)) {
			s = o.star;
			if (up.prob == "*5") {
				// 5倍概率, 通过在普通operator_in_banner[s]中放入5个重复的卡
				operator_in_banner.prob_up[0].push(o);
				operator_in_banner.prob[0] = "*5";
				continue;
			}
			// 直接写占prob概率
			operator_in_banner.prob_up[s].push(o);
			operator_in_banner.prob[s] = up.prob;
		}
		// 非up干员
		else if (o.in_pool == 1) {
			s = o.star;
			operator_in_banner.common[s].push(o);
		}
	}
	console.log(operator_in_banner);
	Show_all_operators();
	return operator_in_banner
}

function Show_all_operators() {
	// 显示所有干员
	$("#show6").html(show_all_names(operator_in_banner.common[6]));
	$("#show5").html(show_all_names(operator_in_banner.common[5]));
	$("#show4").html(show_all_names(operator_in_banner.common[4]));
	$("#show3").html(show_all_names(operator_in_banner.common[3]));

	// 显示限定干员
	$("#show-up").html(""); // reset
	var operator, s;
	if (operator_in_banner.prob[6]) {
		for (i in operator_in_banner.prob_up[6]) {
			operator = operator_in_banner.prob_up[6][i];
			s = '<img class="head-image" src="img/head_image/' + operator.name + '.png" height=50>' + operator.name;
			$("#show-up").append(s);
			Set_border_color($(".head-image:last"), operator.star);
			$("#show6").append(" / " + operator.name);
		}
		$("#show-up").append('<span class="golden">占六星出率的' + operator_in_banner.prob[6] * 100 + "% </span><br/>");
	}
	if (operator_in_banner.prob[0] == "*5") {
		for (i in operator_in_banner.prob_up[0]) {
			operator = operator_in_banner.prob_up[0][i];
			s = '<img class="head-image" src="img/head_image/' + operator.name + '.png" height=50>' + operator.name;
			$("#show-up").append(s);
			Set_border_color($(".head-image:last"), operator.star);
			$("#show6").append(" / " + operator.name);
		}
		$("#show-up").append('<span class="golden">在六星剩余出率中以5倍概率提升</span><br/>');
	}
	if (operator_in_banner.prob[5]) {
		for (i in operator_in_banner.prob_up[5]) {
			operator = operator_in_banner.prob_up[5][i];
			s = '<img class="head-image" src="img/head_image/' + operator.name + '.png" height=50>' + operator.name;
			$("#show-up").append(s);
			Set_border_color($(".head-image:last"), operator.star);
			$("#show5").append(" / " + operator.name);
		}
		$("#show-up").append('<span class="golden">占五星出率的' + operator_in_banner.prob[5] * 100 + "% </span><br/>");
	}
	if (operator_in_banner.prob[4]) {
		for (i in operator_in_banner.prob_up[4]) {
			operator = operator_in_banner.prob_up[4][i];
			s = '<img class="head-image" src="img/head_image/' + operator.name + '.png">' + operator.name;
			$("#show-up").append(s);
			Set_border_color($(".head-image:last"), operator.star);
			$("#show4").append(" / " + operator.name);
		}
		$("#show-up").append('<span class="golden">占四星出率的' + operator_in_banner.prob[4] * 100 + "% </span><br/>");
	}
}

function Set_border_color(obj, star) {
	// 三星 - 白色, 四星 - 紫色, 五星 - 黄色, 六星 - 金色
	let color = ["lightgray", "purple", "khaki", "darkorange"];
	obj.css("border-color", color[star - 3]);
}

function show_own(arr) {
	// 显示已有干员
	if (arr) {
		$("#own").show();
		var s = "";
		for (let i in own) {
			if (i > 0) {
				s += ", ";
			}
			if (own[i].count > 1) {
				s += own[i].name + '<span style="color: gray;">*' + own[i].count + '</span>\t';
			} else {
				s += own[i].name + '\t';
			}
		}
		$("#operators-get").html(s);
	}
}

// 重置所有信息
function reset_data() {
    banner_data = {"_common": {"no_six_star": 0, "p": p_defalt.slice()}};
    store_banner_data();
    own = [];
    store_own_data();
    get_five_star = 10;
    no_six_star = 0;
    p = p_defalt.slice();
    num_get = 0;

    // 重置页面内容
    $("#num5 span").html(get_five_star);
    $("#num5").show();
    $("#num6").html(no_six_star);
    $("#prob6").html(p[3] * 100);
    $("#num-get").html(num_get);
    $("#get1").hide();
    $("#get10").hide();
    $("#own").hide();
}

// 用localStorage储存卡池信息和已有干员信息
function load_banner_data() {
	return JSON.parse(localStorage.getItem("banner_data")) || {"_common": {"no_six_star": 0, "p": p_defalt.slice()}}
}

function store_banner_data(banner) {
	if (banner) {
		if (operator_in_banner.limited) {
			// 限定池保存此卡池的五星和六星保底
			banner_data[banner] = {"get_five_star": get_five_star, "num_get": num_get, "no_six_star": no_six_star, "p": p};
		} else {
			// 常规池保存此卡池的五星保底和公共的六星保底
			banner_data[banner] = {"get_five_star": get_five_star, "num_get": num_get};
			banner_data["_common"] = {"no_six_star": no_six_star, "p": p};
		}
	}
	localStorage.setItem("banner_data", JSON.stringify(banner_data));
	return banner_data
}

function load_own_data() {
	return JSON.parse(localStorage.getItem("own_data")) || []
}

function store_own_data() {
	localStorage.setItem("own_data", JSON.stringify(own));
	return own
}
