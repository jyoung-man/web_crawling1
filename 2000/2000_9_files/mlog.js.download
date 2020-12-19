$(document).ready(
    function () {
        if (MLog.isOnEventAvailable()) {
            $(document).on("click", ".mlog_without_page_change",
                function () {
                    MLog.DATA = $(this).attr("DATA");
                    MLog.init();
                }
            );
            $(document).on("click", ".mlog",
                function (event) {
                    event.preventDefault();
                    MLog.DATA = $(this).attr("DATA");
                    MLog.init(this.href);
                }
            );
        }
    }
);
window.MLog = {
    url: "",
    DATA: "",
    POC_ID: "",
    APP_VERSION: "",
    PORT: "",
    MEMBERKEY: "",
    init: function (url) {
        MLog.buildUrl();
        MLog.sendAjax(url);
    },
    sendAjax: function (url) {
        $.ajax({
            url: MLog.url,
            cache: false,
            async: true,
            dataType: "script",
            complete: function () {
                if (url != "" && url != undefined) {
                    location.href = url;
                }
            }
        });
    },
    buildUrl: function () {
        var queryStrings = "";
        if (MLog.DATA != undefined) {
            queryStrings = MLog.DATA.split("&");
        }
        var list = {};
        for (var i = 0; i < queryStrings.length; i++) {
            var queryStringKeyValue = queryStrings[i].split("=");
            if (queryStringKeyValue.length == 2) {
                list[queryStringKeyValue[0]] = queryStringKeyValue[1];
            }
        }

        var HTTP_OR_HTTPS = "http";
        if (document.URL.indexOf("https") >= 0) {
            HTTP_OR_HTTPS = "https";
        }

        var PORT_STRING = "";
        if (MLog.PORT != "") {
            PORT_STRING = ":" + MLog.PORT;
        }

        var LOG_HOME = "log.melon.com";
        var PHASE = location.host.split("-")[0];

        if(PHASE == "sandbox" || PHASE == "cbt"){
          LOG_HOME = PHASE + "-" + LOG_HOME;
        }

        MLog.url = HTTP_OR_HTTPS + "://" + LOG_HOME + PORT_STRING
            + "?" + MLog.getValue(list["LOG_PRT_CODE"])
            + "&" + MLog.getMemberKey()
            + "&" + MLog.getPocId()
            + "&" + MLog.getAppVersion()
            + "&" + MLog.getPcId();

        if (MLog.getValue(list["LOG_PRT_CODE"]) == "CL" || MLog.getValue(list["LOG_PRT_CODE"]) == "WK" ) {
            MLog.url = MLog.url
                + "&" + MLog.getValue(list["MENU_PRT_CODE"])
                + "&" + MLog.getValue(list["MENU_ID"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE1"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE2"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_TYPE"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE3"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE4"])
                + "&" + MLog.getValue(list["ACTION_AF_CLICK"])
                + "&" + MLog.getValue(list["CLICK_CONTS_PRT_NUMBER"])
                + "&" + MLog.getValue(list["CLICK_CONTS_TYPE_CODE"])
                + "&" + MLog.getValue(list["CLICK_CONTS_ID"])
                + "&" + MLog.getValue(list["RESERVED"])
                + "&" + MLog.getValue(list["PROMO_SEQ"])
                + "&" + MLog.getValue(list["TARGET_APP"])
                + "&" + MLog.getValue(list["PRT_ORDER"])
                + "&" + MLog.getValue(list["WIDGET_SIZE"])
                + "&" + MLog.getValue(list["SEARCH_SUCC_YN"])
                + "&" + MLog.getValue(list["IMPRESSION_ID"])
                + "&" + MLog.getValue(list["SEED_CONTS_TYPE_CODE"])
                + "&" + MLog.getValue(list["SEED_CONTS_ID"]);
        } else if (MLog.getValue(list["LOG_PRT_CODE"]) == -1) {
            MLog.url = MLog.url
                + "&" + MLog.getValue(list["SALE_PRT_CODE_BF_BUY_PHASE"])
                + "&" + MLog.getValue(list["BUY_PHASE"])
                + "&" + MLog.getValue(list["SESSION_ID"])
                + "&" + MLog.getValue(list["SALE_PRT_CODE"])
                + "&" + MLog.getValue(list["PROD_ID"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE"])
                + "&" + MLog.getValue(list["ACTION_TYPE_CODE"])
                + "&" + MLog.getValue(list["BILL_METHD_CODE"])
                + "&" + MLog.getValue(list["RNM_CARD_YN"])
                + "&" + MLog.getValue(list["REG_MDN_YN"])
                + "&" + MLog.getValue(list["PAYMENT_SUCC_YN"])
                + "&" + MLog.getValue(list["BILL_METHD_PAYMENT_FAIL_DESC"])
                + "&" + MLog.getValue(list["ALTER_MESSAGE"])
                + "&" + MLog.getValue(list["TM_ID"])
                + "&" + MLog.getValue(list["RECMD_DISP_IDS"]);
        } else if (MLog.getValue(list["LOG_PRT_CODE"]) == -2) {
            MLog.url = MLog.url
                + "&" + MLog.getValue(list["AREA_PRT_CODE"])
                + "&" + MLog.getValue(list["PHASE_PRT_CODE"])
                + "&" + MLog.getValue(list["SESSION_ID"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE"])
                + "&" + MLog.getValue(list["ACTION_TYPE_CODE"])
                + "&" + MLog.getValue(list["AUTH_INFO_PRT_CODE"])
                + "&" + MLog.getValue(list["AUTH_METHOD_CODE"])
                + "&" + MLog.getValue(list["ALTER_MESSAGE"])
                + "&" + MLog.getValue(list["ADD_VAL1"])
                + "&" + MLog.getValue(list["ADD_VAL2"])
                + "&" + MLog.getValue(list["ADD_VAL3"])
                + "&" + MLog.getValue(list["ADD_VAL4"])
                + "&" + MLog.getValue(list["ADD_VAL5"]);
        } else {
            MLog.url = MLog.url
                + "&" + MLog.getValue(list["MENU_PRT_CODE"])
                + "&" + MLog.getValue(list["MENU_ID_LV1"])
                + "&" + MLog.getValue(list["MENU_ID_LV2"])
                + "&" + MLog.getValue(list["MENU_ID_LV3"])
                + "&" + MLog.getValue(list["MENU_ID_LV4"])
                + "&" + MLog.getValue(list["CLICK_AREA_PRT_CODE"])
                + "&" + MLog.getValue(list["ACTION_AF_CLICK"])
                + "&" + MLog.getValue(list["CLICK_CONTS_TYPE_CODE"])
                + "&" + MLog.getValue(list["CLICK_CONTS_ID"]);
            if (MLog.getValue(list["LOG_PRT_CODE"]) == 1) {
                MLog.url = MLog.url
                    + "&" + MLog.getValue(list["PROMO_CONTS_TYPE_CODE"])
                    + "&" + MLog.getValue(list["PROMO_CONTS_ID"])
                    + "&" + MLog.getValue(list["PROMO_SEQ"])
                    + "&" + MLog.getValue(list["PROMO_DTL_SEQ"]);
            } else if (MLog.getValue(list["LOG_PRT_CODE"]) == 4) {
                MLog.url = MLog.url
                    + "&" + MLog.getValue(list["OUTPOSTING_TYPE_CODE"])
                    + "&" + MLog.getValue(list["OUTPOSTING_TARGET"])
                    + "&" + MLog.getValue(list["EXCEPTION_TYPE_CODE"])
                    + "&" + MLog.getValue(list["MNEWS_SEQ"])
                    + "&" + MLog.getValue(list["ALERT_SET"])
                    + "&" + MLog.getValue(list["GO_TO"]);
            }
        }
    },
    getValue: function (value) {
        if (value == undefined) {
            return "";
        } else {
            return value;
        }
    },
    getMemberKey: function () {
        if (MLog.MEMBERKEY == null || MLog.MEMBERKEY.length == 0) {
            return MLog.getCookie("keyCookie");
        } else {
            return MLog.MEMBERKEY;
        }
    },
    setMemberKey: function (value) {
        MLog.MEMBERKEY = value;
    },
    getPocId: function () {
        if (MLog.POC_ID == null || MLog.POC_ID.length == 0) {
        	if(!MLog.getCookie("MWK_POC") == null || !MLog.getCookie("MWK_POC")  == 0){
       		 	return MLog.getCookie("MWK_POC"); 
        	} else {
        		return MLog.getCookie("POC");
        	}
        } else {
            return MLog.POC_ID;
        }
    },
    setPocId: function (value) {
        MLog.POC_ID = value;
    },
    setAppVersion: function (value) {
        MLog.APP_VERSION = value;
    },
    getAppVersion: function () {
        return MLog.APP_VERSION;
    },
    getPcId: function () {
        return "";
    },
    getCookie: function (cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = $.trim(ca[i]);
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    },
    generateUrlFromNamespace: function (namespace) {
        MLog.DATA = $(namespace).attr("DATA");
        MLog.buildUrl();
        return MLog.url;
    },
    isOnEventAvailable: function () {
        if (typeof jQuery != undefined && jQuery.fn.on != undefined) {
            return true;
        } else {
            return false;
        }
    },
    setPort: function (port) {
        MLog.PORT = port;
    }
};
