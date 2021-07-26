ALTER TABLE `my_dentalplan_db_prod`.`treatment` 
ADD COLUMN `quadrant` VARCHAR(45) NULL DEFAULT NULL AFTER `modified_by`,
ADD COLUMN `tooth` VARCHAR(45) NULL DEFAULT NULL AFTER `quadrant`;

ALTER TABLE `my_dentalplan_db_prod`.`dentalimage` 
CHANGE COLUMN `id` `id` INT(11) NOT NULL ,
ADD COLUMN `provider` INT(11) NULL DEFAULT NULL AFTER `patientname`;

ALTER TABLE `my_dentalplan_db_prod`.`hmoplan` 
ADD COLUMN `groupregion` INT(11) NULL DEFAULT NULL AFTER `planfile`,
ADD COLUMN `welcomeletter` VARCHAR(512) NULL DEFAULT NULL AFTER `groupregion`,
DROP INDEX `hmoplancode` ;


ALTER TABLE `my_dentalplan_db_prod`.`companyhmoplanrate` 
ADD COLUMN `groupregion` INT(11) NULL DEFAULT NULL AFTER `relation`;

ALTER TABLE `my_dentalplan_db_prod`.`urlproperties` 
ADD COLUMN `upgradepolicycallback` VARCHAR(512) NULL DEFAULT NULL AFTER `emailreceipt`;

update groupregion set groupregion = 'ALL' where id = 1;
update urlproperties set upgradepolicycallback = 'http://www.mydentalplan.us/my_dentalplan/policyrenewal/upgrade_policy_callback.html' where id = 1;

to get a list of tables to truncate
====================================
SELECT
    Concat('TRUNCATE TABLE ', CONCAT(TABLE_NAME,';'))
FROM
    INFORMATION_SCHEMA.TABLES
WHERE
    table_schema = 'prod_stg';
    
Backup COmmands Pythonanywhere
==============================
Open Bash Consol

cd
mysqldump -u mydentalplan -h mydentalplan.mysql.pythonanywhere-services.com 'mydentalplan$my_dentalplan_prod'  > db-backup-prod-20190210.sql
mysqldump -u mydentalplan -h mydentalplan.mysql.pythonanywhere-services.com --no-data 'mydentalplan$my_dentalplan_prod'  > db-backup-nodata-prod-20190306.sql
mysqldump -u mydentalplan -h mydentalplan.mysql.pythonanywhere-services.com --no-create-db --no-create-info 'mydentalplan$my_dentalplan_prod'  > db-backup-data-prod-20190306.sql

cd
mysqldump -u StagingServer -h StagingServer.mysql.pythonanywhere-services.com 'StagingServer$prod_stg'  > db-backup-20181208.sql

Required when importing from mySQL 5 to MySQL 8 on Azure VM
================================================
SET GLOBAL log_bin_trust_function_creators = 1;
SET sql_mode = 'NO_UNSIGNED_SUBTRACTION';


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_assignedmembers` AS select 'P' AS `pattype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,`patientmember`.`cell` AS `cell`,`patientmember`.`dob` AS `dob`,`patientmember`.`email` AS `email`,`patientmember`.`enrollmentdate` AS `enrollmentdate`,`patientmember`.`hmopatientmember` AS `hmopatientmember`,`patientmember`.`is_active` AS `is_active`,`patientmember`.`provider` AS `provider`,`company`.`company` AS `company`,`provider`.`providername` AS `providername` from ((`patientmember` left join `company` on((`patientmember`.`company` = `company`.`id`))) left join `provider` on((`patientmember`.`provider` = `provider`.`id`))) union select 'D' AS `pattype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmemberdependants`.`fname` AS `fname`,`patientmemberdependants`.`lname` AS `lname`,`patientmember`.`cell` AS `cell`,`patientmemberdependants`.`depdob` AS `dob`,`patientmember`.`email` AS `email`,`patientmember`.`enrollmentdate` AS `enrollmentdate`,`patientmember`.`hmopatientmember` AS `hmopatientmember`,`patientmember`.`is_active` AS `is_active`,`patientmember`.`provider` AS `provider`,`company`.`company` AS `company`,`provider`.`providername` AS `providername` from (((`patientmemberdependants` left join `patientmember` on((`patientmemberdependants`.`patientmember` = `patientmember`.`id`))) left join `company` on((`company`.`id` = `patientmember`.`company`))) left join `provider` on((`provider`.`id` = `patientmember`.`provider`)));


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_imagememberlist` AS select `patientmember`.`id` AS `id`,`patientmember`.`id` AS `patientid`,`patientmember`.`id` AS `primarypatientid`,`patientmember`.`patientmember` AS `patientmember`,'P' AS `patienttype`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,`patientmember`.`cell` AS `cell`,`patientmember`.`email` AS `email`,`patientmember`.`provider` AS `providerid`,`patientmember`.`is_active` AS `is_active`,1 AS `created_by`,'2016-01-01' AS `created_on`,1 AS `modified_by`,'2016-01-01' AS `modified_on` from `patientmember` union select `patientmemberdependants`.`id` AS `id`,`patientmemberdependants`.`id` AS `patientid`,`patientmemberdependants`.`patientmember` AS `primarypatientid`,`patientmember`.`patientmember` AS `patientmember`,'D' AS `patienttype`,`patientmemberdependants`.`fname` AS `fname`,`patientmemberdependants`.`lname` AS `lname`,`patientmember`.`cell` AS `cell`,`patientmember`.`email` AS `email`,`patientmember`.`provider` AS `providerid`,`patientmemberdependants`.`is_active` AS `is_active`,1 AS `created_by`,'2016-01-01' AS `created_on`,1 AS `modified_by`,'2016-01-01' AS `modified_on` from (`patientmemberdependants` left join `patientmember` on((`patientmember`.`id` = `patientmemberdependants`.`patientmember`))) order by `patientmember`,`patienttype` desc;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_members` AS select 'P' AS `pattype`,`webmember`.`webmember` AS `webmember`,`webmember`.`groupref` AS `groupref`,`webmember`.`fname` AS `fname`,`webmember`.`lname` AS `lname`,`webmember`.`cell` AS `cell`,`webmember`.`webdob` AS `dob`,`webmember`.`email` AS `email`,`webmember`.`status` AS `status`,`webmember`.`webenrolldate` AS `webenrolldate`,`webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,`webmember`.`is_active` AS `is_active`,`webmember`.`provider` AS `providerid`,`webmember`.`company` AS `companyid`,`provider`.`provider` AS `provider`,`company`.`company` AS `company` from ((`webmember` left join `company` on((`webmember`.`company` = `company`.`id`))) left join `provider` on((`webmember`.`provider` = `provider`.`id`))) union select 'D' AS `pattype`,`webmember`.`webmember` AS `webmember`,`webmember`.`groupref` AS `groupref`,`webmemberdependants`.`fname` AS `fname`,`webmemberdependants`.`lname` AS `lname`,`webmember`.`cell` AS `cell`,`webmemberdependants`.`depdob` AS `dob`,`webmember`.`email` AS `email`,`webmember`.`status` AS `status`,`webmember`.`webenrolldate` AS `webenrolldate`,`webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,`webmember`.`is_active` AS `is_active`,`webmember`.`provider` AS `providerid`,`webmember`.`company` AS `companyid`,`provider`.`provider` AS `provider`,`company`.`company` AS `company` from (((`webmemberdependants` left join `webmember` on((`webmemberdependants`.`webmember` = `webmember`.`id`))) left join `company` on((`company`.`id` = `webmember`.`company`))) left join `provider` on((`provider`.`id` = `webmember`.`provider`)));


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_patientmemberdependants` AS select count(`patientmemberdependants`.`id`) AS `dependants`,`patientmemberdependants`.`patientmember` AS `patientmember` from `patientmemberdependants` where (`patientmemberdependants`.`is_active` = 'T') group by `patientmemberdependants`.`patientmember` order by `patientmemberdependants`.`patientmember`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_paymenttxlog` AS select `paymenttxlog`.`txno` AS `txno`,`paymenttxlog`.`txdatetime` AS `txdatetime`,`paymenttxlog`.`txamount` AS `txamount`,`paymenttxlog`.`responsecode` AS `responsecode`,`paymenttxlog`.`responsemssg` AS `responsemssg`,`paymenttxlog`.`paymentid` AS `paymentid`,`paymenttxlog`.`paymentamount` AS `paymentamount`,`paymenttxlog`.`paymentdate` AS `paymentdate`,`paymenttxlog`.`paymenttxid` AS `paymenttxid`,`paymenttxlog`.`servicetax` AS `servicetax`,`paymenttxlog`.`swipecharge` AS `swipecharge`,`paymenttxlog`.`total` AS `total`,`paymenttxlog`.`webmember` AS `webmemberid`,`webmember`.`fname` AS `FirstName`,`webmember`.`lname` AS `LastName`,`webmember`.`webmember` AS `webmember`,`paymenttxlog`.`is_active` AS `is_active`,`company`.`name` AS `companyname`,`company`.`company` AS `companycode` from ((`paymenttxlog` left join `webmember` on((`webmember`.`id` = `paymenttxlog`.`webmember`))) left join `company` on((`company`.`id` = `webmember`.`company`))) order by `company`.`name`;


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_primarypatientlist` AS select 0 AS `id`,'T' AS `patienttype`,'-Select-' AS `fname`,'T' AS `lname`,'T' AS `fullname` union select `patientmember`.`id` AS `id`,'P' AS `patienttype`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,concat(`patientmember`.`fname`,' ',`patientmember`.`lname`) AS `fullname` from `patientmember` union select `patientmemberdependants`.`patientmember` AS `id`,'D' AS `patienttype`,`patientmemberdependants`.`fname` AS `fname`,`patientmemberdependants`.`lname` AS `lname`,concat(`patientmemberdependants`.`fname`,' ',`patientmemberdependants`.`lname`) AS `fullname` from `patientmemberdependants`;


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_treatmentplancost` AS select `treatmentplan`.`primarypatient` AS `primarypatient`,sum(ifnull(`treatmentplan`.`totaltreatmentcost`,0)) AS `totaltreatmentcost`,sum(ifnull(`treatmentplan`.`totalcopay`,0)) AS `totalcopay`,sum(ifnull(`treatmentplan`.`totalinspays`,0)) AS `totalinspays`,(sum(ifnull(`treatmentplan`.`totaltreatmentcost`,0)) - sum(ifnull(`treatmentplan`.`totalinspays`,0))) AS `totalmemberpays` from `treatmentplan` group by `treatmentplan`.`primarypatient`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_webdependantlist` AS select `webmemberdependants`.`webmember` AS `webmember`,`webmemberdependants`.`fname` AS `fname`,`webmemberdependants`.`lname` AS `lname`,`webmemberdependants`.`relation` AS `relation` from `webmemberdependants` where (`webmemberdependants`.`is_active` = 'T') order by `webmemberdependants`.`webmember`;


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_webdependants` AS select count(`webmemberdependants`.`id`) AS `dependants`,`webmemberdependants`.`webmember` AS `webmember` from `webmemberdependants` where (`webmemberdependants`.`is_active` = 'T') group by `webmemberdependants`.`webmember` order by `webmemberdependants`.`webmember`;


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_enrollmentstatus` AS select `webmember`.`webmember` AS `webmember`,`webmember`.`groupref` AS `groupref`,`webmember`.`fname` AS `fname`,`webmember`.`lname` AS `lname`,`webmember`.`status` AS `status`,`provider`.`provider` AS `provider`,`provider`.`providername` AS `providername`,`company`.`id` AS `companyid`,`company`.`company` AS `company`,`hmoplan`.`hmoplancode` AS `hmoplancode`,`webmember`.`cell` AS `cell`,`webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,`webmember`.`is_active` AS `is_active`,ifnull(`vw_webdependants`.`dependants`,0) AS `dependants` from ((((`webmember` left join `vw_webdependants` on((`vw_webdependants`.`webmember` = `webmember`.`id`))) left join `provider` on((`provider`.`id` = `webmember`.`provider`))) left join `company` on((`company`.`id` = `webmember`.`company`))) left join `hmoplan` on((`hmoplan`.`id` = `webmember`.`hmoplan`)));

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_enrollmentstatus1` AS select `webmember`.`id` AS `id`,`webmember`.`webmember` AS `webmember`,`webmember`.`groupref` AS `groupref`,`webmember`.`fname` AS `fname`,`webmember`.`lname` AS `lname`,`webmember`.`status` AS `status`,`provider`.`provider` AS `provider`,`provider`.`providername` AS `providername`,`company`.`id` AS `companyid`,`company`.`company` AS `company`,`hmoplan`.`hmoplancode` AS `hmoplancode`,`webmember`.`cell` AS `cell`,`webmember`.`address1` AS `address1`,`webmember`.`address2` AS `address2`,`webmember`.`address3` AS `address3`,`webmember`.`city` AS `city`,`webmember`.`st` AS `st`,`webmember`.`pin` AS `pin`,`webmember`.`email` AS `email`,`webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,`webmember`.`is_active` AS `is_active`,ifnull(`vw_webdependants`.`dependants`,0) AS `dependants` from ((((`webmember` left join `vw_webdependants` on((`vw_webdependants`.`webmember` = `webmember`.`id`))) left join `provider` on((`provider`.`id` = `webmember`.`provider`))) left join `company` on((`company`.`id` = `webmember`.`company`))) left join `hmoplan` on((`hmoplan`.`id` = `webmember`.`hmoplan`)));

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_memberpayment` AS select `vw_paymenttxlog`.`webmemberid` AS `webmemberid`,`vw_paymenttxlog`.`paymentdate` AS `paymentdate`,sum(`vw_paymenttxlog`.`total`) AS `amount` from `vw_paymenttxlog` where (`vw_paymenttxlog`.`responsecode` = '0') group by `vw_paymenttxlog`.`webmemberid`;


CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_member` AS select 'P' AS `pattype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`mname` AS `mname`,`patientmember`.`lname` AS `lname`,`patientmember`.`dob` AS `dob`,`patientmember`.`cell` AS `cell`,`patientmember`.`telephone` AS `telephone`,`patientmember`.`email` AS `email`,`patientmember`.`status` AS `status`,`patientmember`.`address1` AS `address1`,`patientmember`.`address2` AS `address2`,`patientmember`.`address3` AS `address3`,`patientmember`.`city` AS `city`,`patientmember`.`pin` AS `pin`,`patientmember`.`enrollmentdate` AS `enrollmentdate`,`patientmember`.`terminationdate` AS `terminationdate`,`patientmember`.`premstartdt` AS `premstartdt`,`patientmember`.`premenddt` AS `premenddt`,`patientmember`.`is_active` AS `is_active`,'Self' AS `relation`,ifnull(`vw_patientmemberdependants`.`dependants`,0) AS `dependants`,ifnull(`vw_memberpayment`.`amount`,0) AS `amount`,ifnull(`companyhmoplanrate`.`capitation`,0) AS `membercap`,0 AS `dependantcap`,`provider`.`provider` AS `provider`,`provider`.`providername` AS `providername`,`provider`.`address1` AS `provaddress1`,`provider`.`address2` AS `provaddress2`,`provider`.`address3` AS `provaddress3`,`provider`.`city` AS `provcity`,`provider`.`pin` AS `provpin`,`provider`.`email` AS `provemail`,`provider`.`telephone` AS `provtelephone`,`company`.`id` AS `companyid`,`company`.`company` AS `company`,`hmoplan`.`hmoplancode` AS `hmoplancode`,`hmoplan`.`name` AS `planname`,`agent`.`agent` AS `agent`,`agent`.`name` AS `agentname`,0 AS `agentcommission`,`webmember`.`id` AS `webmemberid`,`vw_memberpayment`.`paymentdate` AS `paymentdate` from (((((((((`patientmember` left join `vw_patientmemberdependants` on((`vw_patientmemberdependants`.`patientmember` = `patientmember`.`id`))) left join `webmember` on((`webmember`.`webmember` = `patientmember`.`patientmember`))) left join `vw_memberpayment` on((`vw_memberpayment`.`webmemberid` = `webmember`.`id`))) left join `provider` on((`provider`.`id` = `patientmember`.`provider`))) left join `company` on((`company`.`id` = `patientmember`.`company`))) left join `hmoplan` on((`hmoplan`.`id` = `patientmember`.`hmoplan`))) left join `agent` on((`agent`.`id` = `company`.`agent`))) left join `agentcommission` on((`agentcommission`.`agent` = `agent`.`id`))) left join `companyhmoplanrate` on(((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`) and (`companyhmoplanrate`.`company` = `patientmember`.`company`) and (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`) and (`companyhmoplanrate`.`relation` = 'Self')))) union select 'D' AS `pattype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmemberdependants`.`fname` AS `fname`,`patientmemberdependants`.`mname` AS `mname`,`patientmemberdependants`.`lname` AS `lname`,`patientmember`.`dob` AS `dob`,`patientmember`.`cell` AS `cell`,`patientmember`.`telephone` AS `telephone`,`patientmember`.`email` AS `email`,`patientmember`.`status` AS `status`,`patientmember`.`address1` AS `address1`,`patientmember`.`address2` AS `address2`,`patientmember`.`address3` AS `address3`,`patientmember`.`city` AS `city`,`patientmember`.`pin` AS `pin`,`patientmember`.`enrollmentdate` AS `enrollmentdate`,`patientmember`.`terminationdate` AS `terminationdate`,`patientmember`.`premstartdt` AS `premstartdt`,`patientmember`.`premenddt` AS `premenddt`,`patientmemberdependants`.`is_active` AS `is_active`,`patientmemberdependants`.`relation` AS `relation`,0 AS `dependants`,0 AS `amount`,0 AS `membercap`,ifnull(`companyhmoplanrate`.`capitation`,0) AS `dependantcap`,`provider`.`provider` AS `provider`,`provider`.`providername` AS `providername`,`provider`.`address1` AS `provaddress1`,`provider`.`address2` AS `provaddress2`,`provider`.`address3` AS `provaddress3`,`provider`.`city` AS `provcity`,`provider`.`pin` AS `provpin`,`provider`.`email` AS `provemail`,`provider`.`telephone` AS `provtelephone`,`company`.`id` AS `companyid`,`company`.`company` AS `company`,`hmoplan`.`hmoplancode` AS `hmoplancode`,`hmoplan`.`name` AS `planname`,`agent`.`agent` AS `agent`,`agent`.`name` AS `agentname`,0 AS `agentcommission`,`webmember`.`id` AS `webmemberid`,`vw_memberpayment`.`paymentdate` AS `paymentdate` from (((((((((`patientmemberdependants` left join `patientmember` on((`patientmemberdependants`.`patientmember` = `patientmember`.`id`))) left join `webmember` on((`webmember`.`webmember` = `patientmember`.`patientmember`))) left join `vw_memberpayment` on((`vw_memberpayment`.`webmemberid` = `webmember`.`id`))) left join `provider` on((`provider`.`id` = `patientmember`.`provider`))) left join `company` on((`company`.`id` = `patientmember`.`company`))) left join `hmoplan` on((`hmoplan`.`id` = `patientmember`.`hmoplan`))) left join `agent` on((`agent`.`id` = `company`.`agent`))) left join `agentcommission` on((`agentcommission`.`agent` = `agent`.`id`))) left join `companyhmoplanrate` on(((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`) and (`companyhmoplanrate`.`company` = `patientmember`.`company`) and (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`) and (`companyhmoplanrate`.`relation` <> 'Self') and (`companyhmoplanrate`.`relation` <> 'T'))));



CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_memberonly` AS select 'P' AS `pattype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`mname` AS `mname`,`patientmember`.`lname` AS `lname`,`patientmember`.`dob` AS `dob`,`patientmember`.`cell` AS `cell`,`patientmember`.`telephone` AS `telephone`,`patientmember`.`email` AS `email`,`patientmember`.`status` AS `status`,`patientmember`.`address1` AS `address1`,`patientmember`.`address2` AS `address2`,`patientmember`.`address3` AS `address3`,`patientmember`.`city` AS `city`,`patientmember`.`pin` AS `pin`,`patientmember`.`enrollmentdate` AS `enrollmentdate`,`patientmember`.`terminationdate` AS `terminationdate`,`patientmember`.`premstartdt` AS `premstartdt`,`patientmember`.`premenddt` AS `premenddt`,`patientmember`.`is_active` AS `is_active`,'Self' AS `relation`,ifnull(`vw_memberpayment`.`amount`,0) AS `amount`,ifnull(`companyhmoplanrate`.`capitation`,0) AS `membercap`,0 AS `dependantcap`,`provider`.`provider` AS `provider`,`provider`.`providername` AS `providername`,`provider`.`address1` AS `provaddress1`,`provider`.`address2` AS `provaddress2`,`provider`.`address3` AS `provaddress3`,`provider`.`city` AS `provcity`,`provider`.`pin` AS `provpin`,`provider`.`email` AS `provemail`,`provider`.`telephone` AS `provtelephone`,`company`.`id` AS `companyid`,`company`.`company` AS `company`,`hmoplan`.`hmoplancode` AS `hmoplancode`,`hmoplan`.`name` AS `planname`,`agent`.`agent` AS `agent`,`agent`.`name` AS `agentname`,0 AS `agentcommission`,`webmember`.`id` AS `webmemberid`,`vw_memberpayment`.`paymentdate` AS `paymentdate` from ((((((((`patientmember` left join `webmember` on((`webmember`.`webmember` = `patientmember`.`patientmember`))) left join `vw_memberpayment` on((`vw_memberpayment`.`webmemberid` = `webmember`.`id`))) left join `provider` on((`provider`.`id` = `patientmember`.`provider`))) left join `company` on((`company`.`id` = `patientmember`.`company`))) left join `hmoplan` on((`hmoplan`.`id` = `patientmember`.`hmoplan`))) left join `agent` on((`agent`.`id` = `company`.`agent`))) left join `agentcommission` on((`agentcommission`.`agent` = `agent`.`id`))) left join `companyhmoplanrate` on(((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`) and (`companyhmoplanrate`.`company` = `patientmember`.`company`) and (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`) and (`companyhmoplanrate`.`relation` = 'Self'))));



PMS2 Report Views
=================
My_PMS2 changes
---------------

CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patienttreatment_header_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`startdate` AS `startdate`,
        `treatmentplan`.`enddate` AS `enddate`,
        `treatmentplan`.`status` AS `status`,
        `treatmentplan`.`patienttype` AS `pattype`,
        `patientmember`.`patientmember` AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `membername`,
        `treatmentplan`.`patientname` AS `patientname`,
        CONCAT(`patientmember`.`cell`,
                '-',
                `patientmember`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `patientmember`.`premenddt` AS `premenddt`
    FROM
        ((((`treatmentplan`
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`patientmember`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
	
	        
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patienttreatment_detail_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`status` AS `status`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`enddate` AS `enddate`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`,
        `dentalprocedure`.`procedurefee` AS `UCR`,
        `treatment`.`quadrant` AS `quadrant`,
        `treatment`.`tooth` AS `tooth`,
        `treatment`.`description` AS `description`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`copay` AS `copay`,
        `treatment`.`inspay` AS `inspay`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))

ALTER TABLE `StagingServer$my_dentalplan_stg`.`treatmentplan` 
ADD COLUMN `totalpaid` DOUBLE NULL AFTER `totalinspays`,
ADD COLUMN `totaldue` DOUBLE NULL AFTER `totalpaid`,
ADD COLUMN `totalcopaypaid` DOUBLE NULL AFTER `totaldue`,
ADD COLUMN `totalinspaid` DOUBLE NULL AFTER `totalcopaypaid`;

ALTER TABLE `mydentalplan$my_dentalplan_prod`.`treatmentplan` 
CHANGE COLUMN `totaltreatmentcost` `totaltreatmentcost` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totalcopay` `totalcopay` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totalinspays` `totalinspays` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totalpaid` `totalpaid` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totaldue` `totaldue` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totalcopaypaid` `totalcopaypaid` DOUBLE NULL DEFAULT 0 ,
CHANGE COLUMN `totalinspaid` `totalinspaid` DOUBLE NULL DEFAULT 0 ;

CREATE TABLE `StagingServer$my_dentalplan_stg`.`payment` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `paymentdate` DATE NULL DEFAULT NULL,
  `amount` DOUBLE NULL DEFAULT 0,
  `paymenttype` VARCHAR(45) NULL DEFAULT NULL,
  `paymentmode` VARCHAR(45) NULL DEFAULT NULL,
  `patientmember` INT(11) NULL DEFAULT NULL,
  `treatmentplan` INT(11) NULL DEFAULT NULL,
   provider INT(11) NULL DEFAULT NULL,
   payor VARCHAR(45) NULL DEFAULT NULL,
  `notes` LONGTEXT NULL DEFAULT NULL,
  paymentcommit CHAR(1) NULL DEFAULT 'F',
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_on` DATETIME NULL DEFAULT NULL,
  `created_by` INT(11) NULL DEFAULT 1,
  `modified_on` DATETIME NULL DEFAULT NULL,
  `modified_by` INT(11) NULL DEFAULT 1,
  PRIMARY KEY (`id`));


  ALTER TABLE `mydentalplan$my_dentalplan_prod`.`payment` 
ADD COLUMN `payor` VARCHAR(45) NULL DEFAULT NULL AFTER `notes`;
ALTER TABLE `mydentalplan$my_dentalplan_prod`.`payment` 
CHANGE COLUMN `type` `paymenttype` VARCHAR(45) NULL DEFAULT NULL ;

ALTER TABLE `mydentalplan$my_dentalplan_prod`.`payment` 
CHANGE COLUMN `mode` `paymentmode` VARCHAR(45) NULL DEFAULT NULL ;

ALTER TABLE `mydentalplan$my_dentalplan_prod`.`payment` 
ADD COLUMN `paymentcommit` CHAR(1) NULL DEFAULT 'F' AFTER `payor`;

ALTER TABLE `mydentalplan$my_dentalplan_prod`.`payment` 
ADD COLUMN `provider` INT(11) NULL DEFAULT NULL AFTER `treatmentplan`;


USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentlist` AS
    SELECT 
        `payment`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `patientmember`.`id` AS `memberid`,
        `payment`.`paymentdate` AS `paymentdate`,
        `payment`.`amount` AS `amount`,
        `payment`.`paymenttype` AS `paymenttype`,
        `payment`.`paymentmode` AS `paymentmode`,
        `payment`.`payor` AS `payor`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        CONCAT(`patientmember`.`fname`,
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `payment`.`is_active` AS `is_active`,
        payment.paymentcommit AS paymentcommit,
        payment.provider as providerid
    FROM
        ((`payment`
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `payment`.`patientmember`)));
        
        
This view has been changed for totalmemberpays
==============================================
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentplancost` AS
    SELECT 
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) AS `totalmemberpays`
    FROM
        `treatmentplan`
    GROUP BY `treatmentplan`.`primarypatient`


USE `mydentalplan$my_dentalplan_prod`;
CREATE  OR REPLACE VIEW `vw_membertreatmentplans_detail_rpt` AS
  SELECT 
        `treatmentplan`.`id` AS `id`,
        treatmentplan.primarypatient AS primarypatient,
        treatmentplan.treatmentplan as treatmentplan,
         treatmentplan.provider as providerid,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`status` AS `status`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`enddate` AS `enddate`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`,
        `dentalprocedure`.`procedurefee` AS `UCR`,
        `treatment`.`quadrant` AS `quadrant`,
        `treatment`.`tooth` AS `tooth`,
        `treatment`.`description` AS `description`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`copay` AS `copay`,
        `treatment`.`inspay` AS `inspay`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
	order  by treatmentplan.id
;

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_header_rpt` AS
    SELECT 
     `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`provider` AS `providerid`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) AS `totalmemberpays`,
        SUM(IFNULL(`treatmentplan`.`totalpaid`, 0)) AS `totalpaid`,
        SUM(IFNULL(`treatmentplan`.`totalcopaypaid`, 0)) AS `totalcopaypaid`,
        SUM(IFNULL(`treatmentplan`.`totalinspaid`, 0)) AS `totalinspaid`,
        SUM(IFNULL(`treatmentplan`.`totaldue`, 0)) AS `totaldue`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `membername`,
        CONCAT(`patientmember`.`cell`,
                '-',
                `patientmember`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `patientmember`.`premenddt` AS `premenddt`
    FROM
        ((((`treatmentplan`
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`patientmember`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
    GROUP BY `treatmentplan`.`primarypatient`;


CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentplanlist` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`startdate` AS `startdate`,
        `treatmentplan`.`status` AS `status`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`provider` AS `provider`,
        `treatmentplan`.`is_active` AS `is_active`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`
    FROM
        (`treatmentplan`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `treatmentplan`.`primarypatient`)))
	
	
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
		`patientmember`.`hmopatientmember` AS `hmopatientmember`,
		`patientmember`.`is_active` AS `is_active`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totaldue` AS `totaldue`
    FROM
        (`patientmember`
        LEFT JOIN `treatmentplan` ON (((`patientmember`.`id` = `treatmentplan`.`primarypatient`) & (`treatmentplan`.`patienttype` = 'P'))));

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`
    FROM
        ((`treatment`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)));
	
CREATE VIEW `vw_appointmentreminders` AS select `t_appointment`.`id` AS `id`,`t_appointment`.`f_title` AS `title`,`t_appointment`.`f_start_time` AS `starttime`,`t_appointment`.`f_end_time` AS `endtime`,`t_appointment`.`f_location` AS `place`,`t_appointment`.`is_active` AS `activeappt`,cast(`t_appointment`.`f_start_time` as date) AS `startdate`,cast(`t_appointment`.`f_end_time` as date) AS `enddate`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,`patientmember`.`email` AS `email`,`patientmember`.`cell` AS `cell`,`patientmember`.`hmopatientmember` AS `hmopatientmember`,`provider`.`providername` AS `providername`,`t_appointment`.`patient` AS `patient`,`t_appointment`.`provider` AS `provider`,`appointmentreminders`.`lastreminder` AS `lastreminder` from (((`t_appointment` left join `patientmember` on((`patientmember`.`id` = `t_appointment`.`patient`))) left join `provider` on((`provider`.`id` = `t_appointment`.`provider`))) left join `appointmentreminders` on((`appointmentreminders`.`appointmentid` = `t_appointment`.`id`)));
CREATE  VIEW `vw_patientmemberappointment` AS select `t_appointment`.`id` AS `id`,`t_appointment`.`f_title` AS `title`,`t_appointment`.`f_start_time` AS `starttime`,`t_appointment`.`f_end_time` AS `endtime`,`t_appointment`.`f_location` AS `location`,`t_appointment`.`is_active` AS `activeappt`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,`patientmember`.`email` AS `email`,`patientmember`.`cell` AS `cell`,`patientmember`.`hmopatientmember` AS `hmopatientmember`,`provider`.`providername` AS `providername`,`t_appointment`.`patient` AS `patient`,`t_appointment`.`provider` AS `provider` from ((`t_appointment` left join `patientmember` on((`patientmember`.`id` = `t_appointment`.`patient`))) left join `provider` on((`provider`.`id` = `t_appointment`.`provider`))) where ((`t_appointment`.`is_active` = 'T') and ((curdate() - interval 30 day) >= `t_appointment`.`f_start_time`) and (`t_appointment`.`f_start_time` <= (curdate() + interval 30 day)));
CREATE  VIEW `vw_patientmemberbirthday` AS select `patientmember`.`id` AS `id`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`groupref` AS `groupref`,`patientmember`.`fname` AS `fname`,`patientmember`.`lname` AS `lname`,`patientmember`.`dob` AS `dob`,`patientmember`.`gender` AS `gender`,`patientmember`.`email` AS `email`,`patientmember`.`cell` AS `cell`,`patientmember`.`provider` AS `provider`,`patientmember`.`company` AS `company`,`patientmember`.`is_active` AS `is_active`,`patientmember`.`hmopatientmember` AS `hmopatientmember`,`provider`.`providername` AS `providername`,`birthdayreminders`.`lastreminder` AS `lastreminder`,str_to_date(concat(year(curdate()),'-',month(`patientmember`.`dob`),'-',dayofmonth(`patientmember`.`dob`)),'%Y-%m-%d') AS `birthday` from ((`patientmember` left join `provider` on((`provider`.`id` = `patientmember`.`provider`))) left join `birthdayreminders` on((`birthdayreminders`.`patient` = `patientmember`.`id`)));



4/26/2017
==========
Create vw_dentalprocedure for PMS2

CREATE 
VIEW `vw_dentalprocedure` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT('  (',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(') ',
                                        CONCAT(CONCAT('( UCR:',
                                                        CONCAT(`dentalprocedure`.`procedurefee`, ')'))))))) AS `shortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
	
Modify vw_memberlist  to add hmoplan and patient information
 CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`is_active` AS `is_active`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        CONCAT_WS(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patient`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `treatmentplan` ON (((`patientmember`.`id` = `treatmentplan`.`primarypatient`) & (`treatmentplan`.`patienttype` = 'P'))))
	
Create Appointment Member List
===================----------=
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointmentmemberlist` AS
    SELECT 
        1 AS `id`,
        1 AS `patientid`,
        1 AS `primarypatientid`,
        'AAA' AS `patientmember`,
        'P' AS `patienttype`,
        'New Patient' AS `fname`,
        ' ' AS `lname`,
        CONCAT('New Patient', ' :') AS `patient`,
        '123' AS `cell`,
        'xxx@mydentalplan.in' AS `email`,
        1 AS `providerid`,
        'T' AS `is_active`,
        'F' AS `hmopatientmember`,
        1 AS `created_by`,
        NOW() AS `created_on`,
        1 AS `modified_by`,
        NOW() AS `modified_on`
    
    UNION SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        `patientmember` 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `id`
    
Modified t_appointment table:
Added 'description' column


Modified vw_treatmentlist : added dentalprocedure.shortdescription  and also vw_treatmentlist in db.py
==================================================================
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        dentalprocedure.shortdescription as shortdescription,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`
    FROM
        ((`treatment`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)));

For Import of DOB and Gender (done on 5/6/2017)
===========================
CREATE TABLE `ximportdata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `memberid` varchar(45) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1561 DEFAULT CHARSET=utf8;


UPDATE patientmember
INNER JOIN ximportdata
    ON patientmember.patientmember = ximportdata.memberid
SET patientmember.dob = ximportdata.dob

5/5/2017
======
USE `mydentalplan$my_dentalplan_prod`;
CREATE  OR REPLACE VIEW `vw_memberpatientlist` AS
  SELECT 
    
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        `patientmember` 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY lname, fname;

5/7/2017  (Staging)
=========
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`treatmentplan` 
CHANGE COLUMN `treatmentplan` `treatmentplan` VARCHAR(64) NULL DEFAULT NULL ;
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`treatment` 
CHANGE COLUMN `treatment` `treatment` VARCHAR(64) NULL DEFAULT NULL ;

===Modify vw_treatmentlist

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`,
        treatmentplan.primarypatient AS memberid,
        treatmentplan.patient as patientid,
        treatmentplan.provider as providerid
    FROM  treatment
    left join dentalprocedure on dentalprocedure.id = treatment.dentalprocedure
    left join treatmentplan on treatmentplan.id = treatment.treatmentplan
 ;

Also modified vw_treatmentlist in db.py

5/11/2017 (Staging)
=========
Added providerid to treatment table.  modified db.py too.
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`treatment` 
ADD COLUMN `provider` INT(11) NULL DEFAULT NULL AFTER `treatmentplan`;

5/13/2017 (Staging)
========
Added fullname in vw_memberpatientlist
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS fullname,
        
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        `patientmember` 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS fullname,
                
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;


5/18/2017
=========
1. Created new table prescription (Staging)
XXXCREATE TABLE `prescription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `medicinename` varchar(45) DEFAULT NULL,
  `medicinecode` varchar(45) DEFAULT NULL,
  `medicineid` int(11) DEFAULT NULL,
  `treatmentid` int(11) DEFAULT NULL,
  `dosage` varchar(45) DEFAULT NULL,
  `frequency` varchar(45) DEFAULT NULL,
  `quantity` varchar(45) DEFAULT NULL,
  `remarks` text,
  `tplanid` int(11) DEFAULT NULL,
  `providerid` int(11) DEFAULT NULL,
  `patientid` int(11) DEFAULT NULL,
  `memberid` int(11) DEFAULT NULL,
  `is_active` char(1) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
2. Created bew table medication (Staging)
XXXCREATE TABLE `medication` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `treatmentid` int(11) DEFAULT NULL,
  `medicinename` varchar(45) DEFAULT NULL,
  `medicinecode` varchar(45) DEFAULT NULL,
  `dosage` varchar(45) DEFAULT NULL,
  `frequency` varchar(45) DEFAULT NULL,
  `quantity` varchar(45) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

3. created new medicaltest (Staging)
XXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`medicaltest` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `treatmentid` INT(11) NULL DEFAULT NULL,
  `tplanid` INT(11) NULL DEFAULT NULL,
  `patientid` INT(11) NULL DEFAULT NULL,
  `memberid` INT(11) NULL DEFAULT NULL,
  `testname` VARCHAR(45) NULL,
  `actualvalue` VARCHAR(45) NULL DEFAULT NULL,
  `lowervalue` VARCHAR(45) NULL DEFAULT NULL,
  `uppervalue` VARCHAR(45) NULL DEFAULT NULL,
  `remarks` LONGTEXT NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_on` DATETIME NULL DEFAULT NULL,
  `created_by` INT(11) NULL DEFAULT NULL,
  `modified_on` DATETIME NULL DEFAULT NULL,
  `modified_by` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`));
ALTER TABLE `mydentalplan$my_dentalplan_prod`.`medicaltest` 
CHANGE COLUMN `actualvalue` `actualval` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `lowervalue` `lowerval` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `uppervalue` `upperval` VARCHAR(45) NULL DEFAULT NULL ,
ADD COLUMN `providerid` INT(11) NULL AFTER `memberid`,
ADD COLUMN `typicalval` VARCHAR(45) NULL AFTER `upperval`;

4. MedNotes (Staging)
XXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`medicalnotes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `treatmentid` INT(11) NULL,
  `providerid` INT(11) NULL,
  `tplanid` INT(11) NULL,
  `patientid` INT(11) NULL,
  `memberid` INT(11) NULL,
  `mednotes` TEXT NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_on` DATETIME NULL,
  `created_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  PRIMARY KEY (`id`));
  
5. Vw Treatmentplan Cost (Staging)
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentplancost` AS
    SELECT 
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalcopay`, 0))) AS `totalmemberpays`
    FROM
        `treatmentplan`
    WHERE
        (`treatmentplan`.`is_active` = 'T')
    GROUP BY `treatmentplan`.`primarypatient`;


6. Modified vw_memberpatientlist (Staging)
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;

7. Modified vw_patientmemberbirthday (Staging)

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientmemberbirthday` AS
    SELECT 
        `vw_memberpatientlist`.`id` AS `id`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`fname` AS `fname`,
        `vw_memberpatientlist`.`lname` AS `lname`,
        `vw_memberpatientlist`.`dob` AS `dob`,
        `vw_memberpatientlist`.`gender` AS `gender`,
        `vw_memberpatientlist`.`email` AS `email`,
        `vw_memberpatientlist`.`cell` AS `cell`,
        `vw_memberpatientlist`.`providerid` AS `providerid`,
        `vw_memberpatientlist`.`is_active` AS `is_active`,
        `vw_memberpatientlist`.`hmopatientmember` AS `hmopatientmember`,
        `provider`.`providername` AS `providername`,
        `birthdayreminders`.`lastreminder` AS `lastreminder`,
        STR_TO_DATE(CONCAT(YEAR(CURDATE()),
                        '-',
                        MONTH(`vw_memberpatientlist`.`dob`),
                        '-',
                        DAYOFMONTH(`vw_memberpatientlist`.`dob`)),
                '%Y-%m-%d') AS `birthday`
    FROM
        ((`vw_memberpatientlist`
        LEFT JOIN `provider` ON ((`provider`.`id` = `vw_memberpatientlist`.`providerid`)))
        LEFT JOIN `birthdayreminders` ON ((`birthdayreminders`.`patient` = `vw_memberpatientlist`.`patientid`)));

8. vw_appointmentreminders (Staging)
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointmentreminders` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `title`,
        `t_appointment`.`f_start_time` AS `starttime`,
        `t_appointment`.`f_end_time` AS `endtime`,
        `t_appointment`.`f_location` AS `place`,
        `t_appointment`.`is_active` AS `activeappt`,
        CAST(`t_appointment`.`f_start_time` AS DATE) AS `startdate`,
        CAST(`t_appointment`.`f_end_time` AS DATE) AS `enddate`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`fname` AS `fname`,
        `vw_memberpatientlist`.`lname` AS `lname`,
        `vw_memberpatientlist`.`email` AS `email`,
        `vw_memberpatientlist`.`cell` AS `gender`,
        `vw_memberpatientlist`.`gender` AS `cell`,
        `vw_memberpatientlist`.`hmopatientmember` AS `hmopatientmember`,
       
        `t_appointment`.`patient` AS `patient`,
        `t_appointment`.`provider` AS `provider`,
        `appointmentreminders`.`lastreminder` AS `lastreminder`
    FROM
        (((`t_appointment`
        LEFT JOIN `vw_memberpatientlist` ON ((`vw_memberpatientlist`.`patientid` = `t_appointment`.`patient`)))
         LEFT JOIN `appointmentreminders` ON ((`appointmentreminders`.`appointmentid` = `t_appointment`.`id`))));

8. Time Zone


Python's datetime is not timezone aware. now() will always return the system time which, on PythonAnywhere, is UTC. If you want timezone info on a datetime, you need to use timezone aware datetimes by providing tzinfo. pytz can help with that.
Staff glenn | 2359 posts | PythonAnywhere staff| | July 12, 2016, 11:01 a.m. | permalink


9. Patientmember, Patientmemberdependants, vw_memberpatientlist,vw_memberlist (Staging)

Added New Member, FreeTratment, premenddt column (boolean)

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmember` 
ADD COLUMN `freetreatment` CHAR(1) NULL DEFAULT 'T' AFTER `renewed`;

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmember` 
ADD COLUMN `freetreatment` CHAR(1) NULL DEFAULT 'T' AFTER `newmember`;


XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmemberdependants` 
ADD COLUMN `newmember` CHAR(1) NULL DEFAULT 'T' AFTER `webdepid`;

XXXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmemberdependants` 
ADD COLUMN `freetreatment` CHAR(1) NULL DEFAULT 'T' AFTER `newmember`;




USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        patientmember.premenddt AS premenddt,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
		patientmember.premenddt AS premenddt,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;

USE `mydentalplan$my_dentalplan_prod`; 
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        patientmember.newmember AS newmember,
        patientmember.freetreatment AS freetreatment,
        patientmember.premenddt AS premenddt,
        
        `patientmember`.`is_active` AS `is_active`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        CONCAT_WS(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patient`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `treatmentplan` ON (((`patientmember`.`id` = `treatmentplan`.`primarypatient`) & (`treatmentplan`.`patienttype` = 'P'))));

10. XXXUpdate Patientmember/patientmemberdependants table with newmember = True (Staging)

11. Add free dentalprocedure to table dentalprocedure (Staging)

12. Create vw_dentalprocedure_x999 (Staging)
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_x999` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT('  (',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(') ',
                                        CONCAT(CONCAT('( UCR:',
                                                        CONCAT(`dentalprocedure`.`procedurefee`, ')'))))))) AS `shortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`dentalprocedure` = 'X999')
	
#this view is to display only Free Initial Consulting & Cleaning (X999 is the procedure code)
db.define_table('vw_dentalprocedure_x999',
                Field('id', 'integer'),
                Field('shortdescription',  'string'),
                Field('procedurefee', 'double'),
                Field('is_active','boolean',default=True)
                )
db.vw_dentalprocedure_x999._singular = "vw_dentalprocedure_x999"
db.vw_dentalprocedure_x999._plural   = "vw_dentalprocedure_x999"

13. Update COntrib/Common.py and other modules (Staging)

14. Added premstartdt in vw_memberpatientlist (Staging)
USE `mydentalplan$my_dentalplan_prod`;
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;

6/5/2017  (Charting) (Staging)
==============================
1. New Charting Table. Need to modify db.py too
XXXX
CREATE TABLE `mydentalplan$my_dentalplan_prod`.`dentalchart` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `provider` INT(11) NULL DEFAULT NULL,
  `treatmentplan` INT(11) NULL DEFAULT NULL,
  `treatment` INT(11) NULL DEFAULT NULL,
  `patientmember` INT(11) NULL DEFAULT NULL,
  `patient` INT(11) NULL,
  `patienttype` VARCHAR(1) NULL DEFAULT NULL,
  `patientname` VARCHAR(128) NULL DEFAULT NULL,
  `title` VARCHAR(128) NULL DEFAULT NULL,
  `chartfile` VARCHAR(512) NULL DEFAULT NULL,
  `chartdate` DATE NULL DEFAULT NULL,
  `description` LONGTEXT NULL DEFAULT NULL,
  `t1` VARCHAR(512) NULL DEFAULT NULL,
  `t2` VARCHAR(512) NULL DEFAULT NULL,
  `t3` VARCHAR(512) NULL DEFAULT NULL,
  `t4` VARCHAR(512) NULL DEFAULT NULL,
  `t5` VARCHAR(512) NULL DEFAULT NULL,
  `t6` VARCHAR(512) NULL DEFAULT NULL,
  `t7` VARCHAR(512) NULL DEFAULT NULL,
  `t8` VARCHAR(512) NULL DEFAULT NULL,
  `t9` VARCHAR(512) NULL DEFAULT NULL,
  `t10` VARCHAR(512) NULL DEFAULT NULL,
  `t11` VARCHAR(512) NULL DEFAULT NULL,
  `t12` VARCHAR(512) NULL DEFAULT NULL,
  `t13` VARCHAR(512) NULL DEFAULT NULL,
  `t14` VARCHAR(512) NULL DEFAULT NULL,
  `t15` VARCHAR(512) NULL DEFAULT NULL,
  `t16` VARCHAR(512) NULL DEFAULT NULL,
  `t17` VARCHAR(512) NULL DEFAULT NULL,
  `t18` VARCHAR(512) NULL DEFAULT NULL,
  `t19` VARCHAR(512) NULL DEFAULT NULL,
  `t20` VARCHAR(512) NULL DEFAULT NULL,
  `t21` VARCHAR(512) NULL DEFAULT NULL,
  `t22` VARCHAR(512) NULL DEFAULT NULL,
  `t23` VARCHAR(512) NULL DEFAULT NULL,
  `t24` VARCHAR(512) NULL DEFAULT NULL,
  `t25` VARCHAR(512) NULL DEFAULT NULL,
  `t26` VARCHAR(512) NULL DEFAULT NULL,
  `t27` VARCHAR(512) NULL DEFAULT NULL,
  `t28` VARCHAR(512) NULL DEFAULT NULL,
  `t29` VARCHAR(512) NULL DEFAULT NULL,
  `t30` VARCHAR(512) NULL DEFAULT NULL,
  `t31` VARCHAR(512) NULL DEFAULT NULL,
  `t32` VARCHAR(512) NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_on` DATETIME NULL DEFAULT NULL,
  `created_by` INT(11) NULL DEFAULT NULL,
  `modified_on` DATETIME NULL DEFAULT NULL,
  `modified_by` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`));


6/15/2017
==========
1. Add an inactive blank company record for non-member  (Staging)
YYYYY - XXXINSERT INTO company
(
`company`,
`name`,
`is_active`
)
VALUES
(
' ',
'XXX',
'F' );

2. YYYY Replace all Bangalore, Bengalaru with Bengaluru in City.  (Staging)
3. Modified Db.py

4. Modified vw_membertreatmentplans_detail_rpt  (Staging)
===============================================
USE `mydentalplan$my_dentalplan_prod`;
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_detail_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`status` AS `status`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`enddate` AS `enddate`,
        `dentalprocedure`.`dentalprocedure` AS `dentalprocedure`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`,
        `dentalprocedure`.`procedurefee` AS `UCR`,
        `treatment`.`quadrant` AS `quadrant`,
        `treatment`.`tooth` AS `tooth`,
        `treatment`.`description` AS `description`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`copay` AS `copay`,
        `treatment`.`inspay` AS `inspay`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON (((`treatment`.`treatmentplan` = `treatmentplan`.`id`) & (`treatment`.`is_active` = 'T'))))
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `vw_memberpatientlist` ON ((((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T'))))
    ORDER BY `treatmentplan`.`id`

5. Modified vw_memberpatientlist - added company,hmoplan field (Staging)
=======================================================
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
         patientmember.hmoplan as hmoplan,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
         patientmember.hmoplan as hmoplan,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`


6. vw_membertreatmentplans_header_rpt  changes (Staging)
==============================================
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_header_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`provider` AS `providerid`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) AS `totalmemberpays`,
        SUM(IFNULL(`treatmentplan`.`totalpaid`, 0)) AS `totalpaid`,
        SUM(IFNULL(`treatmentplan`.`totalcopaypaid`, 0)) AS `totalcopaypaid`,
        SUM(IFNULL(`treatmentplan`.`totalinspaid`, 0)) AS `totalinspaid`,
        SUM(IFNULL(`treatmentplan`.`totaldue`, 0)) AS `totaldue`,
        CONCAT(`vw_memberpatientlist`.`fname`,
                ' ',
                `vw_memberpatientlist`.`lname`,
                ' (',
                `vw_memberpatientlist`.`patientmember`,
                ')') AS `membername`,
        CONCAT(`vw_memberpatientlist`.`cell`,
                '-',
                `vw_memberpatientlist`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `vw_memberpatientlist`.`premenddt` AS `premenddt`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        (((((`treatmentplan`
        LEFT JOIN `vw_memberpatientlist` ON ((((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T'))))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`vw_memberpatientlist`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`vw_memberpatientlist`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
    GROUP BY `treatmentplan`.`patient`
    
    
7. Chnage to Patientmember and Patientmemberdependants (Staging)
======================================================
YYYXXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmember` 
CHANGE COLUMN `freetreatment` `freetreatment` CHAR(1) NULL DEFAULT 'F' ;


YYYYXXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`patientmemberdependants` 
CHANGE COLUMN `freetreatment` `freetreatment` CHAR(1) NULL DEFAULT 'F' ;

YYY8. States.py - Normalized Bengaluru
====================================

YYY9. Common.py - getproviderfromid
=================================

10. Modified vw_memberpatientlist 09/03/2017)
=============================================
Added regionid (for patientmember.groupregion) field.

11. Modified peregister table (09/06/2017)
==========================================
Added company referece field

12. Created Medical Notes tabl (09/24/2017)
============================================
New table created 
XXXCREATE TABLE `medicalnotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `patientid` int(11) DEFAULT NULL,
  `memberid` int(11) DEFAULT NULL,
  `notesdate` date DEFAULT NULL,
  `occupation` varchar(45) DEFAULT NULL,
  `resoff` varchar(45) DEFAULT NULL,
  `referer` varchar(45) DEFAULT NULL,
  `bp` char(1) DEFAULT NULL,
  `diabetes` char(1) DEFAULT NULL,
  `anaemia` char(1) DEFAULT NULL,
  `epilepsy` char(1) DEFAULT NULL,
  `asthma` char(1) DEFAULT NULL,
  `sinus` char(1) DEFAULT NULL,
  `heart` char(1) DEFAULT NULL,
  `jaundice` char(1) DEFAULT NULL,
  `tb` char(1) DEFAULT NULL,
  `cardiac` char(1) DEFAULT NULL,
  `arthritis` char(1) DEFAULT NULL,
  `anyother` char(1) DEFAULT NULL,
  `allergic` char(1) DEFAULT NULL,
  `excessivebleeding` char(1) DEFAULT NULL,
  `seriousillness` char(1) DEFAULT NULL,
  `hospitalized` char(1) DEFAULT NULL,
  `medications` char(1) DEFAULT NULL,
  `surgery` char(1) DEFAULT NULL,
  `pregnant` char(1) DEFAULT NULL,
  `breastfeeding` char(1) DEFAULT NULL,
  `anyothercomplaint` longtext,
  `chiefcomplaint` longtext,
  `duration` longtext,
  `is_active` char(1) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


10/08/2017 - Altered vw_paymentlist
====================================

10/08/2017 - Create vw_treatmentplansummary and vw_paymentsummary1
==============================================================
CREATE 
 
VIEW `vw_treatmentplansummary` AS
    SELECT 
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`provider` AS `provider`,
        `treatmentplan`.`is_active` AS `is_active`,
        SUM(`treatmentplan`.`totaltreatmentcost`) AS `totalcost`
    FROM
        `treatmentplan`
    WHERE
        (`treatmentplan`.`is_active` = 'T')
    GROUP BY `treatmentplan`.`primarypatient` , `treatmentplan`.`provider`
    
    
CREATE 
    
VIEW `vw_paymentsummary1` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`provider` AS `provider`,
        SUM(`payment`.`amount`) AS `totalpaid`,
        `vw_treatmentplansummary`.`totalcost` AS `totalcost`
    FROM
        (`payment`
        LEFT JOIN `vw_treatmentplansummary` ON ((`payment`.`patientmember` = `vw_treatmentplansummary`.`memberid`)))
    GROUP BY `payment`.`patientmember`    
    
10/12/2017 - Role, Speciality, Doctor, doctortimings
=====================================
XXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`role` (
  `id` INT(11) NOT NULL,
  `role` VARCHAR(45) NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));


XXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`doctor` (
  `id` INT(11) NULL AUTO_INCREMENT,
  `name` VARCHAR(128) NULL,
  `speciality` INT(11) NULL,
  `role` INT(11) NULL,
  `email` VARCHAR(128) NULL,
  `cell` VARCHAR(45) NULL,
  `registration` VARCHAR(45) NULL,
  `color` VARCHAR(45) NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));

XXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`speciality` (
  `id` INT(11) NULL,
  `speciality` VARCHAR(128) NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));


XXXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`doctortiming` (
  `id` INT(11) NULL AUTO_INCREMENT,
  `doctor` INT(11) NULL,
  `startdate` DATETIME NULL,
  `enddate` DATETIME NULL,
  `is_active` CHAR(1) NULL,
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));



Added officestaff to status.py in gluon/contrib
Added weekdays, ams, pms to gluon/contrib/cycle.py

XXXXCREATE TABLE `doctortiming` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doctor` int(11) DEFAULT NULL,
  `mon_day_chk` char(1) DEFAULT NULL,
  `mon_lunch_chk` char(1) DEFAULT NULL,
  `mon_del_chk` char(1) DEFAULT NULL,
  `mon_starttime_1` varchar(45) DEFAULT NULL,
  `mon_endtime_1` varchar(45) DEFAULT NULL,
  `mon_starttime_2` varchar(45) DEFAULT NULL,
  `mon_endtime_2` varchar(45) DEFAULT NULL,
  `mon_visitinghours` varchar(128) DEFAULT NULL,
  `tue_day_chk` char(1) DEFAULT NULL,
  `tue_lunch_chk` char(1) DEFAULT NULL,
  `tue_del_chk` char(1) DEFAULT NULL,
  `tue_starttime_1` varchar(45) DEFAULT NULL,
  `tue_endtime_1` varchar(45) DEFAULT NULL,
  `tue_starttime_2` varchar(45) DEFAULT NULL,
  `tue_endtime_2` varchar(45) DEFAULT NULL,
  `tue_visitinghours` varchar(128) DEFAULT NULL,
  `wed_day_chk` char(1) DEFAULT NULL,
  `wed_lunch_chk` char(1) DEFAULT NULL,
  `wed_del_chk` char(1) DEFAULT NULL,
  `wed_starttime_1` varchar(45) DEFAULT NULL,
  `wed_endtime_1` varchar(45) DEFAULT NULL,
  `wed_starttime_2` varchar(45) DEFAULT NULL,
  `wed_endtime_2` varchar(45) DEFAULT NULL,
  `wed_visitinghours` varchar(128) DEFAULT NULL,
  `thu_day_chk` char(1) DEFAULT NULL,
  `thu_lunch_chk` char(1) DEFAULT NULL,
  `thu_del_chk` char(1) DEFAULT NULL,
  `thu_starttime_1` varchar(45) DEFAULT NULL,
  `thu_endtime_1` varchar(45) DEFAULT NULL,
  `thu_starttime_2` varchar(45) DEFAULT NULL,
  `thu_endtime_2` varchar(45) DEFAULT NULL,
  `thu_visitinghours` varchar(128) DEFAULT NULL,
  `fri_day_chk` char(1) DEFAULT NULL,
  `fri_lunch_chk` char(1) DEFAULT NULL,
  `fri_del_chk` char(1) DEFAULT NULL,
  `fri_starttime_1` varchar(45) DEFAULT NULL,
  `fri_endtime_1` varchar(45) DEFAULT NULL,
  `fri_starttime_2` varchar(45) DEFAULT NULL,
  `fri_endtime_2` varchar(45) DEFAULT NULL,
  `fri_visitinghours` varchar(128) DEFAULT NULL,
  `sat_day_chk` char(1) DEFAULT NULL,
  `sat_lunch_chk` char(1) DEFAULT NULL,
  `sat_del_chk` char(1) DEFAULT NULL,
  `sat_starttime_1` varchar(45) DEFAULT NULL,
  `sat_endtime_1` varchar(45) DEFAULT NULL,
  `sat_starttime_2` varchar(45) DEFAULT NULL,
  `sat_endtime_2` varchar(45) DEFAULT NULL,
  `sat_visitinghours` varchar(128) DEFAULT NULL,
  `sun_day_chk` char(1) DEFAULT NULL,
  `sun_lunch_chk` char(1) DEFAULT NULL,
  `sun_del_chk` char(1) DEFAULT NULL,
  `sun_starttime_1` varchar(45) DEFAULT NULL,
  `sun_endtime_1` varchar(45) DEFAULT NULL,
  `sun_starttime_2` varchar(45) DEFAULT NULL,
  `sun_endtime_2` varchar(45) DEFAULT NULL,
  `sun_visitinghours` varchar(128) DEFAULT NULL,
  `visitinghours` varchar(128) DEFAULT NULL,
  `is_active` char(1) DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

Modified t_appointment table - added doctor id
================================================
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`t_appointment` 
ADD COLUMN `doctor` INT(11) NULL DEFAULT NULL AFTER `provider`;

USE `mydentalplan$my_dentalplan_prod`;
CREATE  OR REPLACE VIEW `vw_doctorapptmnts` AS
select t_appointment.doctor, count(*)  AS doctorappts, t_appointment.provider as apptprovider, t_appointment.f_start_time AS starttime from t_appointment group by f_start_time, doctor;

USE `mydentalplan$my_dentalplan_prod`;
CREATE  OR REPLACE VIEW `vw_doctorsappointments` AS
select doctor.name, doctor.color, count(vw_doctorapptmnts.doctorappts) as appts from doctor 
left join vw_doctorapptmnts on doctor.id = vw_doctorapptmnts.doctor and doctor.providerid = vw_doctorapptmnts.apptprovider;


XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`treatment` 
ADD COLUMN `doctor` INT(11) NULL DEFAULT NULL AFTER `provider`;

XXXCREATE TABLE `mydentalplan$my_dentalplan_prod`.`medicine` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `medicine` VARCHAR(128) NULL,
  `strength` VARCHAR(45) NULL,
  `strengthuom` VARCHAR(45) NULL,
  `medicinetype` VARCHAR(45) NULL,
  `instructions` VARCHAR(128) NULL,
  `is_active` CHAR(1) NULL,
  `created_on` DATETIME NULL,
  `created_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  PRIMARY KEY (`id`));

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`medicine` 
ADD COLUMN `providerid` INT(11) NULL AFTER `id`;

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`medicine` 
ADD COLUMN `notes` MEDIUMTEXT NULL AFTER `instructions`;

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`prescription` 
ADD COLUMN `doctorid` INT(11) NULL DEFAULT NULL AFTER `providerid`;


USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientprescription` AS
    SELECT 
        `prescription`.`id` AS `id`,
        `prescription`.`providerid` AS `providerid`,
        `prescription`.`dosage` AS `dosage`,
        `prescription`.`frequency` AS `frequency`,
        `prescription`.`quantity` AS `quantity`,
        `prescription`.`remarks` AS `remarks`,
        `prescription`.`prescriptiondate` AS `prescriptiondate`,
        `medicine`.`medicine` AS `medicine`,
        `medicine`.`medicinetype` AS `medicinetype`,
        `medicine`.`strength` AS `strength`,
        `medicine`.`strengthuom` AS `strengthuom`,
        `medicine`.`instructions` AS `instructions`,
        `prescription`.`patientid` AS `patientid`,
        `prescription`.`memberid` AS `memberid`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`dob` AS `dob`,
        (YEAR(NOW()) - YEAR(`vw_memberpatientlist`.`dob`)) AS `age`,
        `vw_memberpatientlist`.`gender` AS `gender`,
        `doctor`.`id` AS `doctorid`,
        `doctor`.`name` AS `doctorname`,
        `prescription`.`is_active` AS `is_active`
    FROM
        (((`prescription`
        LEFT JOIN `medicine` ON (((`medicine`.`id` = `prescription`.`medicineid`)
            AND (`prescription`.`providerid` = `medicine`.`providerid`)
            AND (`prescription`.`is_active` = 'T'))))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`providerid` = `prescription`.`providerid`)
            AND (`vw_memberpatientlist`.`patientid` = `prescription`.`patientid`)
            AND (`vw_memberpatientlist`.`primarypatientid` = `prescription`.`memberid`))))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `prescription`.`doctorid`)));

	
	
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`prescription` 
ADD COLUMN `prescriptiondate` DATE NULL AFTER `memberid`;

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,        
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
		(YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,        
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;

USE `mydentalplan$my_dentalplan_prod`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`;

11/05/2017
===========
vw_dentalprocedure_x999
USE `production`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_x999` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,        
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`dentalprocedure` = 'X999');


2) set freetreatment = F by default for patientmember and dependants in db


11/7/2017 : Import Plan Rates
=============================

SELECT * FROM StagingServer$my_dentalplan_prod.importplanrates;

ALTER TABLE `importplanrates` 
DROP COLUMN `regionid`,
DROP COLUMN `planid`,
DROP COLUMN `companyid`,
ADD COLUMN `Covered` INT(11) NULL AFTER `Relation`;


ALTER TABLE `importplanrates` 
ADD COLUMN `companyid` INT(11) NULL AFTER `Capitation`,
ADD COLUMN `planid` INT(11) NULL AFTER `companyid`,
ADD COLUMN `regionid` INT(11) NULL AFTER `planid`;


UPDATE importplanrates imp, company cmp
SET imp.companyid = cmp.id
WHERE cmp.company = imp.company;

UPDATE importplanrates imp, hmoplan hmp
SET imp.planid = hmp.id
WHERE hmp.hmoplancode = imp.plan;

UPDATE importplanrates imp, groupregion rgn
SET imp.regionid = rgn.id
WHERE rgn.groupregion = imp.Region;

update companyhmoplanrate cmph, importplanrates imp
set cmph.is_active = 'F' 
WHERe cmph.company = imp.companyid

insert into companyhmoplanrate (covered, premium, capitation, companypays, company, hmoplan, is_active, created_on, created_by, modified_on, modified_by, relation,groupregion)
select covered, premium, capitation, companypays, companyid, planid, 'T', Now(), 1, now(), 1, relation,regionid from importplanrates


11/11/2017 - Dental Chart Changes
==================================
XXXXX1. Dental Chart
CREATE TABLE `dentalchart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `patientid` int(11) DEFAULT NULL,
  `memberid` int(11) DEFAULT NULL,
  `providerid` int(11) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


xxxxx2. Tooth
CREATE TABLE `tooth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `toothnumber` int(11) DEFAULT '0',
  `chartid` int(11) DEFAULT NULL,
  `doctorid` int(11) DEFAULT NULL,
  `procedureid` int(11) DEFAULT NULL,
  `treatmentid` int(11) DEFAULT NULL,
  `section` varchar(45) DEFAULT NULL,
  `chartdate` date DEFAULT NULL,
  `notes` mediumtext,
  `is_active` char(1) DEFAULT 'T',
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE `production`.`dentalprocedure` 
ADD COLUMN `in_chart` CHAR(1) NULL DEFAULT 'F' AFTER `modified_by`,
ADD COLUMN `chartcolor` VARCHAR(45) NULL DEFAULT NULL AFTER `in_chart`;
ALTER TABLE `production`.`dentalprocedure` 
CHANGE COLUMN `chartcolor` `chartcolor` VARCHAR(45) NULL DEFAULT NULL AFTER `procedurefee`,
CHANGE COLUMN `in_chart` `for_chart` CHAR(1) NULL DEFAULT 'F' AFTER `chartcolor`;

ALTER TABLE `production`.`tooth` 
ADD COLUMN `toothid` VARCHAR(45) NULL AFTER `id`,
ADD COLUMN `p9` VARCHAR(45) NULL AFTER `toothid`,
ADD COLUMN `p1` VARCHAR(45) NULL DEFAULT NULL AFTER `modified_by`,
ADD COLUMN `p2` VARCHAR(45) NULL DEFAULT NULL AFTER `p1`,
ADD COLUMN `p3` VARCHAR(45) NULL DEFAULT NULL AFTER `p2`,
ADD COLUMN `p4` VARCHAR(45) NULL DEFAULT NULL AFTER `p3`,
ADD COLUMN `p5` VARCHAR(45) NULL DEFAULT NULL AFTER `p4`,
ADD COLUMN `p6` VARCHAR(45) NULL DEFAULT NULL AFTER `p5`,
ADD COLUMN `p7` VARCHAR(45) NULL DEFAULT NULL AFTER `p6`,
ADD COLUMN `p8` VARCHAR(45) NULL DEFAULT NULL AFTER `p7`,
ADD COLUMN `l1` VARCHAR(45) NULL DEFAULT NULL AFTER `p8`,
ADD COLUMN `l2` VARCHAR(45) NULL DEFAULT NULL AFTER `l1`,
ADD COLUMN `l3` VARCHAR(45) NULL DEFAULT NULL AFTER `l2`,
ADD COLUMN `l4` VARCHAR(45) NULL DEFAULT NULL AFTER `l3`,
ADD COLUMN `e1` VARCHAR(45) NULL DEFAULT NULL AFTER `l4`;

XXXXXUSE `production`;
CREATE 
  
VIEW `vw_dentalprocedure_chart` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`chartcolor` AS `chartcolor`,
        `dentalprocedure`.`for_chart` AS `for_chart`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`for_chart` = 'T')  AND (dentalprocedure.is_active  = 'T');

XXXXUSE `production`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_tooth` AS
    SELECT 
        `tooth`.`id` AS `id`,
        `tooth`.`toothid` AS `toothid`,
        `tooth`.`toothnumber` AS `toothnumber`,
        `tooth`.`toothsection` AS `toothsection`,
        `tooth`.`chartdate` AS `chartdate`,
        `tooth`.`notes` AS `notes`,
        tooth.p1 AS p1,
        tooth.p2 AS p2,
        tooth.p3 AS p3,
        tooth.p4 AS p4,
        tooth.p5 AS p5,
        tooth.p6 AS p6,
        tooth.p7 AS p7,
        tooth.p8 AS p8,
        tooth.p9 AS p9,
        tooth.l1 AS l1,
        tooth.l2 AS l2,
        tooth.l3 AS l3,
        tooth.l4 AS l4,
        tooth.e1 AS e1,
        `tooth`.`is_active` AS `activetooth`,
        `doctor`.`name` AS `doctorname`,
        `vw_dentalprocedure_chart`.`id` AS `procedureid`,
        `vw_dentalprocedure_chart`.`shortdescription` AS `shortdescription`,
        `vw_dentalprocedure_chart`.`altshortdescription` AS `altshortdescription`,
        `vw_dentalprocedure_chart`.`chartcolor` AS `chartcolor`,
        `provider`.`id` AS `providerid`,
        `dentalchart`.`id` AS `dentalchartid`,
        `treatment`.`id` AS `treatmentid`,
        `vw_memberpatientlist`.`patientid` AS `patientid`,
        `vw_memberpatientlist`.`primarypatientid` AS `memberid`
    FROM
        ((((((`tooth`
        LEFT JOIN `dentalchart` ON (((`dentalchart`.`id` = `tooth`.`chartid`)
            AND (`dentalchart`.`is_active` = 'T'))))
        LEFT JOIN `provider` ON ((`dentalchart`.`providerid` = `provider`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON (((`dentalchart`.`patientid` = `vw_memberpatientlist`.`patientid`)
            AND (`dentalchart`.`memberid` = `vw_memberpatientlist`.`primarypatientid`))))
        LEFT JOIN `vw_dentalprocedure_chart` ON ((`vw_dentalprocedure_chart`.`id` = `tooth`.`procedureid`)))
        LEFT JOIN `doctor` ON (((`doctor`.`id` = `tooth`.`doctorid`)
            AND (`doctor`.`is_active` = 'T'))))
        LEFT JOIN `treatment` ON (((`treatment`.`id` = `tooth`.`treatmentid`)
            AND (`treatment`.`is_active` = 'T'))));

11/13/2017 : tooth color table
==============================
CREATE TABLE `production`.`toothcolor` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `toothid` VARCHAR(45) NULL,
  `procedureid` INT(11) NULL,
  `providerid` INT(11) NULL,
  `p1` VARCHAR(45) NULL,
  `p2` VARCHAR(45) NULL,
  `p3` VARCHAR(45) NULL,
  `p4` VARCHAR(45) NULL,
  `p5` VARCHAR(45) NULL,
  `p6` VARCHAR(45) NULL,
  `p7` VARCHAR(45) NULL,
  `p8` VARCHAR(45) NULL,
  `p9` VARCHAR(45) NULL,
  `l1` VARCHAR(45) NULL,
  `l2` VARCHAR(45) NULL,
  `l3` VARCHAR(45) NULL,
  `l4` VARCHAR(45) NULL,
  `e1` VARCHAR(45) NULL,
  `is_active` CHAR(1) NULL,
  `created_on` DATETIME NULL,
  `created_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  PRIMARY KEY (`id`));


11/23/2017 - PricePlan - for Procedure cost as per the plan addition
=====================================================================

XXXX CREATE TABLE `prod_dup`.`procedurepriceplan` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `procedurepriceplancode` VARCHAR(45) NULL DEFAULT NULL,
  `procedurecode` VARCHAR(45) NULL DEFAULT NULL,
  `ucrfee` DOUBLE NULL DEFAULT 0,
  `procedurefee` DOUBLE NULL DEFAULT 0,
  `copay` DOUBLE NULL DEFAULT 0,
  `companypays` DOUBLE NULL DEFAULT 0,
  `inspays` DOUBLE NULL DEFAULT 0,
  `is_active` CHAR(1) NULL DEFAULT '1',
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));

XXXXALTER TABLE `prod_dup`.`procedurepriceplan` 
ADD COLUMN `providerid` INT(11) NULL AFTER `id`;



XXXX ALTER TABLE `prod_dup`.`hmoplan` 
ADD COLUMN `procedurepriceplancode` VARCHAR(45) NULL AFTER `name`;


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_hmoprocedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`is_active` AS `is_active`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`
    FROM
        ((`procedurepriceplan`
        LEFT JOIN `hmoplan` ON (((`hmoplan`.`procedurepriceplancode` = `procedurepriceplan`.`procedurepriceplancode`)&(`hmoplan`.`is_active` = 'T'))))
        LEFT JOIN `dentalprocedure` ON (((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)& (`dentalprocedure`.`is_active` = 'T'))));


ALTER TABLE `prod_dup`.`dentalprocedure` 
ADD COLUMN `category` CHAR(1) NULL DEFAULT 'G' AFTER `dentalprocedure`;

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`;


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_chart` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`dentalprocedure` AS `proccode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`chartcolor` AS `chartcolor`,
        `dentalprocedure`.`for_chart` AS `for_chart`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        ((`dentalprocedure`.`for_chart` = 'T')
            AND (`dentalprocedure`.`is_active` = 'T'));

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_x999` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`dentalprocedure` AS `proccode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`dentalprocedure` = 'X999');


Add Remarks column in Dental Procedure

XXXX ALTER TABLE `prod_dup`.`procedurepriceplan` 
ADD COLUMN `remarks` VARCHAR(45) NULL AFTER `inspays`;


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_x999` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`dentalprocedure` AS `proccode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`dentalprocedure` = 'G0100A');
ALTER TABLE `prod_dup`.`dentalprocedure` 
CHANGE COLUMN `shortdescription` `shortdescription` VARCHAR(512) NULL DEFAULT NULL ;

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        'T' AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ':',
                CONCAT(`procedurepriceplan`.`procedurecode`,
                        ':',
                        CONCAT(`procedurepriceplan`.`ucrfee`,
                                ':',
                                CONCAT(`procedurepriceplan`.`procedurefee`,
                                        ':',
                                        CONCAT(`procedurepriceplan`.`copay`,
                                                ':',
                                                CONCAT(`procedurepriceplan`.`inspays`,
                                                        ':',
                                                        CONCAT(`procedurepriceplan`.`companypays`,
                                                                ':',
                                                                CONCAT(`procedurepriceplan`.`id`, 'T')))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));




USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan_x999` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ':',
                CONCAT(`procedurepriceplan`.`procedurecode`,
                        ':',
                        CONCAT(`procedurepriceplan`.`ucrfee`,
                                ':',
                                CONCAT(`procedurepriceplan`.`procedurefee`,
                                        ':',
                                        CONCAT(`procedurepriceplan`.`copay`,
                                                ':',
                                                CONCAT(`procedurepriceplan`.`inspays`,
                                                        ':',
                                                        CONCAT(`procedurepriceplan`.`companypays`,
                                                                ':',
                                                                CONCAT(`procedurepriceplan`.`id`, 'T')))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))
    WHERE
        (`procedurepriceplan`.`is_free` = 'T');




REmove Dentalprocedure foreign key restrainin Treatment


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)));

ALTER TABLE `prod_dup`.`procedurepriceplan` 
ADD COLUMN `is_free` CHAR(1) NULL DEFAULT 'F' AFTER `remarks`;

ALTER TABLE `prod_dup`.`dentalprocedure` 
CHANGE COLUMN `for_chart` `for_chart` CHAR(1) NULL DEFAULT 'F' AFTER `procedurefee`,
CHANGE COLUMN `chartcolor` `chartcolor` VARCHAR(45) NULL DEFAULT NULL AFTER `for_chart`,
CHANGE COLUMN `remarks` `remarks` VARCHAR(45) NULL DEFAULT NULL AFTER `chartcolor`,
ADD COLUMN `is_free` CHAR(1) NULL DEFAULT 'F' AFTER `remarks`;

CREATE TABLE `dentalprocedure_chart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `procedurecode` varchar(45) DEFAULT NULL,
  `description` varchar(512) DEFAULT NULL,
  `color` varchar(45) DEFAULT NULL,
  `is_active` char(1) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE `prod_dup`.`dentalprocedure_chart` 
ADD COLUMN `providerid` INT(11) NULL AFTER `color`;


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_chart` AS
   SELECT 
        `dentalprocedure_chart`.`id` AS `id`,
        `dentalprocedure_chart`.`procedurecode` AS `proccode`,
        CONCAT(`dentalprocedure_chart`.`description`,
                CONCAT(':',
                        CONCAT(`dentalprocedure_chart`.`procedurecode`,
                                 CONCAT(':', CONCAT(`dentalprocedure_chart`.`id`))))) AS `shortdescription`,
        `dentalprocedure_chart`.`description` AS `altshortdescription`,
        `dentalprocedure_chart`.`description` AS `description`,
         0 AS `procedurefee`,
        `dentalprocedure_chart`.`color` AS `chartcolor`,
        'T' AS `for_chart`,
        `dentalprocedure_chart`.`is_active` AS `is_active`
    FROM
        `dentalprocedure_chart`
    WHERE
    (`dentalprocedure_chart`.`is_active` = 'T');


USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_chart` AS
    SELECT 
        `dentalprocedure_chart`.`id` AS `id`,
        `dentalprocedure_chart`.`providerid` AS `providerid`,
        `dentalprocedure_chart`.`procedurecode` AS `proccode`,
        CONCAT(`dentalprocedure_chart`.`description`,
                CONCAT(':',
                        CONCAT(`dentalprocedure_chart`.`procedurecode`,
                                CONCAT(':',
                                        CONCAT(`dentalprocedure_chart`.`id`))))) AS `shortdescription`,
        `dentalprocedure_chart`.`description` AS `altshortdescription`,
        `dentalprocedure_chart`.`description` AS `description`,
        0 AS `procedurefee`,
        `dentalprocedure_chart`.`color` AS `chartcolor`,
        'T' AS `for_chart`,
        `dentalprocedure_chart`.`is_active` AS `is_active`
    FROM
        `dentalprocedure_chart`
    WHERE
        (`dentalprocedure_chart`.`is_active` = 'T');


12/22/2017
==========

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_payment_treatmentplan_treatment` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`is_active` AS `tplanactive`,
        `treatmentplan`.`treatmentplan` AS `tplan`,
        `dentalprocedure`.`shortdescription` AS `shortdescription`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `procedurepriceplan` ON ((`procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));


ALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `registration` VARCHAR(128) NULL AFTER `groupregion`;

Made changes to common.py


10012018 - Wed Jan 2018 - Modifications to New Treatment
=========================================================
XXXXCREATE TABLE `treatment_procedure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `treatmentid` int(11) DEFAULT NULL,
  `dentalprocedure` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `treatmentplan__idx` (`treatment_id`),
  KEY `procedurecode__idx` (`dentalprocedure`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

XXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `quadrant` VARCHAR(45) NULL AFTER `dentalprocedure`,
ADD COLUMN `tooth` VARCHAR(45) NULL AFTER `quadrant`;

XXXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `treatmentdate` DATE NULL AFTER `tooth`;

XXXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `is_active` CHAR(1) NULL DEFAULT 'T' AFTER `treatmentdate`;

XXXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `ucr` DOUBLE NULL AFTER `is_active`,
ADD COLUMN `procedurefee` DOUBLE NULL AFTER `ucr`,
ADD COLUMN `copay` DOUBLE NULL AFTER `procedurefee`,
ADD COLUMN `inspays` DOUBLE NULL AFTER `copay`,
ADD COLUMN `companypays` DOUBLE NULL AFTER `inspays`;

XXXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `remarks` VARCHAR(512) NULL AFTER `companypays`;


USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `vw_procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `vw_procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `vw_procedurepriceplan`.`copay` AS `copay`,
        `vw_procedurepriceplan`.`inspays` AS `inspays`,
        `vw_procedurepriceplan`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));
	
USE `prod_dup`;
XXXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`remarks` AS `remarks`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));
	
XXXXCREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan_x999` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`) AS `shortdescription`,
		
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))
    WHERE
        (`procedurepriceplan`.`is_free` = 'T');


XXXXCREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `vw_procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `vw_procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)))

XXXALTER TABLE `prod_dup`.`treatment` 
ADD COLUMN `companypay` DOUBLE NULL DEFAULT NULL AFTER `inspay`;

XXXALTER TABLE `prod_dup`.`treatment` 
ADD COLUMN `actualtreatmentcost` DOUBLE NULL DEFAULT NULL AFTER `status`;

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_payment_treatmentplan_treatment` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`is_active` AS `tplanactive`,
        `treatmentplan`.`treatmentplan` AS `tplan`,
        `treatment`.`treatment` AS `treatment`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))));


USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentlist` AS
    SELECT 
        `payment`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `patientmember`.`id` AS `memberid`,
        `payment`.`paymentdate` AS `paymentdate`,
        `payment`.`amount` AS `amount`,
        `payment`.`paymenttype` AS `paymenttype`,
        `payment`.`paymentmode` AS `paymentmode`,
        `payment`.`payor` AS `payor`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `payment`.`is_active` AS `is_active`,
        `payment`.`paymentcommit` AS `paymentcommit`,
        `payment`.`provider` AS `providerid`,
        treatment.treatment AS treatment
    FROM
        (((`payment`
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `payment`.`patientmember`)));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_detail_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`status` AS `status`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`enddate` AS `enddate`,
        `treatment`.`quadrant` AS `quadrant`,
        `treatment`.`tooth` AS `tooth`,
        `treatment`.`description` AS `description`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
         treatment.actualtreatmentcost AS actualtreatmentcost,
        `treatment`.`copay` AS `copay`,
        `treatment`.`inspay` AS `inspay`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        (((`treatmentplan`
        LEFT JOIN `treatment` ON (((`treatment`.`treatmentplan` = `treatmentplan`.`id`) & (`treatment`.`is_active` = 'T'))))
        LEFT JOIN `vw_memberpatientlist` ON ((((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T')))))
    order by treatmentplan.id;

XXXCREATE TABLE `role_default` (
  `id` int(11) NOT NULL,
  `role` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

XXXCREATE TABLE `speciality_default` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `speciality` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

XXXCREATE TABLE `prod_dup`.`medicine_default` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `medicine` VARCHAR(45) NULL,
  `meditype` VARCHAR(45) NULL,
  `strength` VARCHAR(45) NULL,
  `strngthuom` VARCHAR(45) NULL,
  `instructions` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`));

XXXXCREATE TABLE `prod_dup`.`casereport` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `patientid` INT(11) NULL,
  `providerid` INT(11) NULL,
  `doctorid` INT(11) NULL,
  `casereport` LONGTEXT NULL,
  `is_active` CHAR(1) NULL,
  `created_on` DATETIME NULL,
  `created_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  PRIMARY KEY (`id`));

USE `prod_dup`;
XXXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_casereport` AS
    SELECT 
        `casereport`.`id` AS `id`,
        casereport.providerid as providerid,
        casereport.patientid as patientid,
        `casereport`.`casereport` AS `casereport`,
        `doctor`.`name` AS `doctorname`,
        `provider`.`providername` AS `providername`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `casereport`.`is_active` AS `is_active`,
        `casereport`.`modified_on` AS `modified_on`,
        `casereport`.`modified_by` AS `modified_by`
    FROM
        (((`casereport`
        LEFT JOIN `doctor` ON ((`casereport`.`doctorid` = `doctor`.`id`)))
        LEFT JOIN `provider` ON ((`casereport`.`providerid` = `provider`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON ((`casereport`.`patientid` = `vw_memberpatientlist`.`patientid`)));


20-01-2018 - Changes as per feedback
=====================================
XXXXUSE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_header_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`provider` AS `providerid`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) AS `totalmemberpays`,
        SUM(IFNULL(`treatmentplan`.`totalpaid`, 0)) AS `totalpaid`,
        SUM(IFNULL(`treatmentplan`.`totalcopaypaid`, 0)) AS `totalcopaypaid`,
        SUM(IFNULL(`treatmentplan`.`totalinspaid`, 0)) AS `totalinspaid`,
        SUM(IFNULL(`treatmentplan`.`totaldue`, 0)) AS `totaldue`,
        `vw_memberpatientlist`.`email` AS memberemail,
        `vw_memberpatientlist`.`cell` AS membercell,
        CONCAT(`vw_memberpatientlist`.`fname`,
                ' ',
                `vw_memberpatientlist`.`lname`,
                ' (',
                `vw_memberpatientlist`.`patientmember`,
                ')') AS `membername`,
        CONCAT(`vw_memberpatientlist`.`cell`,
                '-',
                `vw_memberpatientlist`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `vw_memberpatientlist`.`premenddt` AS `premenddt`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        (((((`treatmentplan`
        LEFT JOIN `vw_memberpatientlist` ON ((((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T'))))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`vw_memberpatientlist`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`vw_memberpatientlist`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
    GROUP BY `treatmentplan`.`patient`;

XXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `cell` VARCHAR(45) NULL DEFAULT NULL AFTER `patient`;
XXXXALTER TABLE `prod_dup`.`t_appointment_archive` 
ADD COLUMN `cell` VARCHAR(45) NULL DEFAULT NULL AFTER `doctor`;

25-01-2018 : Changes after call with Dhimant
============================================

XXXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `f_patientname` VARCHAR(128) NULL DEFAULT NULL AFTER `f_title`;
XXXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `f_duration` VARCHAR(45) NULL DEFAULT NULL AFTER `f_end_time`;
XXXXALTER TABLE `prod_dup`.`t_appointment` 
CHANGE COLUMN `f_duration` `f_duration` INT(11) NULL DEFAULT NULL ;
XXXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `f_treatmentid` INT(11) NULL DEFAULT NULL AFTER `f_location`;

XXUSE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
        order by treatment.id desc;
XXXXALTER TABLE `prod_dup`.`treatment` 
ADD COLUMN `chiefcomplaint` VARCHAR(128) NULL AFTER `tooth`;

USE `prod_dup`;
USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
    ORDER BY `treatment`.`id` DESC;

01/29/2018 - Title
==================

XXXALTER TABLE `prod_dup`.`patientmember` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `dob`;

XXXALTER TABLE `prod_dup`.`patientmemberdependants` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `id`;

XXXALTER TABLE `prod_dup`.`doctor` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `id`;

XXXALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `provider`;

XXXALTER TABLE `prod_dup`.`webmember` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `webmember`;

XXXALTER TABLE `prod_dup`.`webmemberdependants` 
ADD COLUMN `title` VARCHAR(45) NULL AFTER `id`;


XXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `ptitle` VARCHAR(45) NULL AFTER `f_title`;

XXXXALTER TABLE `prod_dup`.`treatmentplan` 
ADD COLUMN `pattitle` VARCHAR(45) NULL AFTER `patienttype`;



XXXXCREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_member` AS
    SELECT 
        'P' AS `pattype`,
        `patientmember`.`id` AS `patientmemberid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`mname` AS `mname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`telephone` AS `telephone`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`status` AS `status`,
        `patientmember`.`address1` AS `address1`,
        `patientmember`.`address2` AS `address2`,
        `patientmember`.`address3` AS `address3`,
        `patientmember`.`city` AS `city`,
        `patientmember`.`pin` AS `pin`,
        `patientmember`.`enrollmentdate` AS `enrollmentdate`,
        `patientmember`.`terminationdate` AS `terminationdate`,
        `patientmember`.`premstartdt` AS `premstartdt`,
        `patientmember`.`premenddt` AS `premenddt`,
        `patientmember`.`is_active` AS `is_active`,
        'Self' AS `relation`,
        IFNULL(`vw_patientmemberdependants`.`dependants`,
                0) AS `dependants`,
        IFNULL(`vw_memberpayment`.`amount`, 0) AS `amount`,
        IFNULL(`companyhmoplanrate`.`capitation`, 0) AS `membercap`,
        0 AS `dependantcap`,
        `provider`.`provider` AS `provider`,
        `provider`.`providername` AS `providername`,
        `provider`.`address1` AS `provaddress1`,
        `provider`.`address2` AS `provaddress2`,
        `provider`.`address3` AS `provaddress3`,
        `provider`.`city` AS `provcity`,
        `provider`.`pin` AS `provpin`,
        `provider`.`email` AS `provemail`,
        `provider`.`telephone` AS `provtelephone`,
        `company`.`id` AS `companyid`,
        `company`.`company` AS `company`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`name` AS `planname`,
        `agent`.`agent` AS `agent`,
        `agent`.`name` AS `agentname`,
        0 AS `agentcommission`,
        `webmember`.`id` AS `webmemberid`,
        `vw_memberpayment`.`paymentdate` AS `paymentdate`,
        `companyhmoplanrate`.`is_active` AS `chractive`
    FROM
        (((((((((`patientmember`
        LEFT JOIN `vw_patientmemberdependants` ON ((`vw_patientmemberdependants`.`patientmember` = `patientmember`.`id`)))
        LEFT JOIN `webmember` ON ((`webmember`.`webmember` = `patientmember`.`patientmember`)))
        LEFT JOIN `vw_memberpayment` ON ((`vw_memberpayment`.`webmemberid` = `webmember`.`id`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `patientmember`.`provider`)))
        LEFT JOIN `company` ON ((`company`.`id` = `patientmember`.`company`)))
        LEFT JOIN `hmoplan` ON ((`hmoplan`.`id` = `patientmember`.`hmoplan`)))
        LEFT JOIN `agent` ON ((`agent`.`id` = `company`.`agent`)))
        LEFT JOIN `agentcommission` ON ((`agentcommission`.`agent` = `agent`.`id`)))
        LEFT JOIN `companyhmoplanrate` ON (((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`)
            AND (`companyhmoplanrate`.`company` = `patientmember`.`company`)
            AND (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`)
            AND (`companyhmoplanrate`.`relation` = 'Self')))) 
    UNION SELECT 
        'D' AS `pattype`,
        `patientmemberdependants`.`id` AS `patientmemberid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`mname` AS `mname`,
        `patientmemberdependants`.`lname` AS `lname`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`telephone` AS `telephone`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`status` AS `status`,
        `patientmember`.`address1` AS `address1`,
        `patientmember`.`address2` AS `address2`,
        `patientmember`.`address3` AS `address3`,
        `patientmember`.`city` AS `city`,
        `patientmember`.`pin` AS `pin`,
        `patientmember`.`enrollmentdate` AS `enrollmentdate`,
        `patientmember`.`terminationdate` AS `terminationdate`,
        `patientmember`.`premstartdt` AS `premstartdt`,
        `patientmember`.`premenddt` AS `premenddt`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmemberdependants`.`relation` AS `relation`,
        0 AS `dependants`,
        0 AS `amount`,
        0 AS `membercap`,
        IFNULL(`companyhmoplanrate`.`capitation`, 0) AS `dependantcap`,
        `provider`.`provider` AS `provider`,
        `provider`.`providername` AS `providername`,
        `provider`.`address1` AS `provaddress1`,
        `provider`.`address2` AS `provaddress2`,
        `provider`.`address3` AS `provaddress3`,
        `provider`.`city` AS `provcity`,
        `provider`.`pin` AS `provpin`,
        `provider`.`email` AS `provemail`,
        `provider`.`telephone` AS `provtelephone`,
        `company`.`id` AS `companyid`,
        `company`.`company` AS `company`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`name` AS `planname`,
        `agent`.`agent` AS `agent`,
        `agent`.`name` AS `agentname`,
        0 AS `agentcommission`,
        `webmember`.`id` AS `webmemberid`,
        `vw_memberpayment`.`paymentdate` AS `paymentdate`,
        `companyhmoplanrate`.`is_active` AS `chractive`
    FROM
        (((((((((`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmemberdependants`.`patientmember` = `patientmember`.`id`)))
        LEFT JOIN `webmember` ON ((`webmember`.`webmember` = `patientmember`.`patientmember`)))
        LEFT JOIN `vw_memberpayment` ON ((`vw_memberpayment`.`webmemberid` = `webmember`.`id`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `patientmember`.`provider`)))
        LEFT JOIN `company` ON ((`company`.`id` = `patientmember`.`company`)))
        LEFT JOIN `hmoplan` ON ((`hmoplan`.`id` = `patientmember`.`hmoplan`)))
        LEFT JOIN `agent` ON ((`agent`.`id` = `company`.`agent`)))
        LEFT JOIN `agentcommission` ON ((`agentcommission`.`agent` = `agent`.`id`)))
        LEFT JOIN `companyhmoplanrate` ON (((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`)
            AND (`companyhmoplanrate`.`company` = `patientmember`.`company`)
            AND (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`)
            AND (`companyhmoplanrate`.`relation` <> 'Self')
            AND (`companyhmoplanrate`.`relation` <> 'T'))))
    WHERE
        (`patientmember`.`hmopatientmember` = 'T')
	
USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`patientmember` AS `patientmember`,
        patientmember.title as title,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        `patientmember`.`premenddt` AS `premenddt`,
        `patientmember`.`is_active` AS `is_active`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        CONCAT_WS(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patient`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `treatmentplan` ON (((`patientmember`.`id` = `treatmentplan`.`primarypatient`) & (`treatmentplan`.`patienttype` = 'P'))));


USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberonly` AS
    SELECT 
        'P' AS `pattype`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
		`patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`mname` AS `mname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`telephone` AS `telephone`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`status` AS `status`,
        `patientmember`.`address1` AS `address1`,
        `patientmember`.`address2` AS `address2`,
        `patientmember`.`address3` AS `address3`,
        `patientmember`.`city` AS `city`,
        `patientmember`.`pin` AS `pin`,
        `patientmember`.`enrollmentdate` AS `enrollmentdate`,
        `patientmember`.`terminationdate` AS `terminationdate`,
        `patientmember`.`premstartdt` AS `premstartdt`,
        `patientmember`.`premenddt` AS `premenddt`,
        `patientmember`.`is_active` AS `is_active`,
        'Self' AS `relation`,
        IFNULL(`vw_memberpayment`.`amount`, 0) AS `amount`,
        IFNULL(`companyhmoplanrate`.`capitation`, 0) AS `membercap`,
        0 AS `dependantcap`,
        `provider`.`provider` AS `provider`,
        `provider`.`providername` AS `providername`,
        `provider`.`address1` AS `provaddress1`,
        `provider`.`address2` AS `provaddress2`,
        `provider`.`address3` AS `provaddress3`,
        `provider`.`city` AS `provcity`,
        `provider`.`pin` AS `provpin`,
        `provider`.`email` AS `provemail`,
        `provider`.`telephone` AS `provtelephone`,
        `company`.`id` AS `companyid`,
        `company`.`company` AS `company`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`name` AS `planname`,
        `agent`.`agent` AS `agent`,
        `agent`.`name` AS `agentname`,
        0 AS `agentcommission`,
        `webmember`.`id` AS `webmemberid`,
        `vw_memberpayment`.`paymentdate` AS `paymentdate`
    FROM
        ((((((((`patientmember`
        LEFT JOIN `webmember` ON ((`webmember`.`webmember` = `patientmember`.`patientmember`)))
        LEFT JOIN `vw_memberpayment` ON ((`vw_memberpayment`.`webmemberid` = `webmember`.`id`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `patientmember`.`provider`)))
        LEFT JOIN `company` ON ((`company`.`id` = `patientmember`.`company`)))
        LEFT JOIN `hmoplan` ON ((`hmoplan`.`id` = `patientmember`.`hmoplan`)))
        LEFT JOIN `agent` ON ((`agent`.`id` = `company`.`agent`)))
        LEFT JOIN `agentcommission` ON ((`agentcommission`.`agent` = `agent`.`id`)))
        LEFT JOIN `companyhmoplanrate` ON (((`companyhmoplanrate`.`hmoplan` = `patientmember`.`hmoplan`)
            AND (`companyhmoplanrate`.`company` = `patientmember`.`company`)
            AND (`companyhmoplanrate`.`groupregion` = `patientmember`.`groupregion`)
            AND (`companyhmoplanrate`.`relation` = 'Self'))));


USE `prod_dup`;
XXXX     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
         patientmember.title as title,        
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        patientmemberdependants.title as title,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        'T' AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `lname` , `fname`;

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientmember` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`patientmember` AS `patientmember`,
        patientmember.title as title,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`
    FROM
        `patientmember`;


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientmemberappointment` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `title`,
        `t_appointment`.`f_start_time` AS `starttime`,
        `t_appointment`.`f_end_time` AS `endtime`,
        `t_appointment`.`f_location` AS `location`,
        `t_appointment`.`is_active` AS `activeappt`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
         patientmember.title as ptitle,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `provider`.`providername` AS `providername`,
        `t_appointment`.`patient` AS `patient`,
        `t_appointment`.`provider` AS `provider`
    FROM
        ((`t_appointment`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `t_appointment`.`patient`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `t_appointment`.`provider`)))
    WHERE
        ((`t_appointment`.`is_active` = 'T')
            AND ((CURDATE() - INTERVAL 30 DAY) >= `t_appointment`.`f_start_time`)
            AND (`t_appointment`.`f_start_time` <= (CURDATE() + INTERVAL 30 DAY)));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientmemberbirthday` AS
    SELECT 
        `vw_memberpatientlist`.`id` AS `id`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        vw_memberpatientlist.title as title,
        `vw_memberpatientlist`.`fname` AS `fname`,
        `vw_memberpatientlist`.`lname` AS `lname`,
        `vw_memberpatientlist`.`dob` AS `dob`,
        `vw_memberpatientlist`.`gender` AS `gender`,
        `vw_memberpatientlist`.`email` AS `email`,
        `vw_memberpatientlist`.`cell` AS `cell`,
        `vw_memberpatientlist`.`providerid` AS `providerid`,
        `vw_memberpatientlist`.`is_active` AS `is_active`,
        `vw_memberpatientlist`.`hmopatientmember` AS `hmopatientmember`,
        `provider`.`providername` AS `providername`,
        `birthdayreminders`.`lastreminder` AS `lastreminder`,
        STR_TO_DATE(CONCAT(YEAR(CURDATE()),
                        '-',
                        MONTH(`vw_memberpatientlist`.`dob`),
                        '-',
                        DAYOFMONTH(`vw_memberpatientlist`.`dob`)),
                '%Y-%m-%d') AS `birthday`
    FROM
        ((`vw_memberpatientlist`
        LEFT JOIN `provider` ON ((`provider`.`id` = `vw_memberpatientlist`.`providerid`)))
        LEFT JOIN `birthdayreminders` ON ((`birthdayreminders`.`patient` = `vw_memberpatientlist`.`patientid`)));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientprescription` AS
    SELECT 
        `prescription`.`id` AS `id`,
        `prescription`.`providerid` AS `providerid`,
        `prescription`.`dosage` AS `dosage`,
        `prescription`.`frequency` AS `frequency`,
        `prescription`.`quantity` AS `quantity`,
        `prescription`.`remarks` AS `remarks`,
        `prescription`.`prescriptiondate` AS `prescriptiondate`,
        `medicine`.`id` AS `medicineid`,
        `medicine`.`medicine` AS `medicine`,
        `medicine`.`medicinetype` AS `medicinetype`,
        `medicine`.`strength` AS `strength`,
        `medicine`.`strengthuom` AS `strengthuom`,
        `medicine`.`instructions` AS `instructions`,
        `prescription`.`patientid` AS `patientid`,
        `prescription`.`memberid` AS `memberid`,
        `vw_memberpatientlist`.`title` AS `title`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`dob` AS `dob`,
        (YEAR(NOW()) - YEAR(`vw_memberpatientlist`.`dob`)) AS `age`,
        `vw_memberpatientlist`.`gender` AS `gender`,
        `doctor`.`id` AS `doctorid`,
        doctor.title as doctitle,
        `doctor`.`name` AS `doctorname`,
        `prescription`.`is_active` AS `is_active`
    FROM
        (((`prescription`
        LEFT JOIN `medicine` ON (((`medicine`.`id` = `prescription`.`medicineid`)
            AND (`prescription`.`providerid` = `medicine`.`providerid`)
            AND (`prescription`.`is_active` = 'T'))))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`providerid` = `prescription`.`providerid`)
            AND (`vw_memberpatientlist`.`patientid` = `prescription`.`patientid`)
            AND (`vw_memberpatientlist`.`primarypatientid` = `prescription`.`memberid`))))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `prescription`.`doctorid`)));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patienttreatment_header_rpt` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`startdate` AS `startdate`,
        `treatmentplan`.`enddate` AS `enddate`,
        `treatmentplan`.`status` AS `status`,
        `treatmentplan`.`patienttype` AS `pattype`,
        `patientmember`.`patientmember` AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        patientmember.title as title,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `membername`,
        `treatmentplan`.`patientname` AS `patientname`,
        CONCAT(`patientmember`.`cell`,
                '-',
                `patientmember`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `patientmember`.`premenddt` AS `premenddt`
    FROM
        ((((`treatmentplan`
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`patientmember`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)));

USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentlist` AS
    SELECT 
        `payment`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `patientmember`.`id` AS `memberid`,
        `payment`.`paymentdate` AS `paymentdate`,
        `payment`.`amount` AS `amount`,
        `payment`.`paymenttype` AS `paymenttype`,
        `payment`.`paymentmode` AS `paymentmode`,
        `payment`.`payor` AS `payor`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        patientmember.title as title,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `payment`.`is_active` AS `is_active`,
        `payment`.`paymentcommit` AS `paymentcommit`,
        `payment`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`
    FROM
        (((`payment`
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `payment`.`patientmember`)));

USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_primarypatientlist` AS
    SELECT 
        0 AS `id`,
        0 AS `auxid`,
        'T' AS `patienttype`,
        ' ' AS title,
        '-Select-' AS `fname`,
        'T' AS `lname`,
        'T' AS `fullname`
    
    UNION SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `auxid`,
        'P' AS `patienttype`,
        patientmember.title as title,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`
    FROM
        `patientmember` 
    UNION SELECT 
        `patientmemberdependants`.`patientmember` AS `id`,
        `patientmemberdependants`.`id` AS `auxid`,
        'D' AS `patienttype`,
        patientmemberdependants.title as title,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`
    FROM
        `patientmemberdependants`;


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_members` AS
    SELECT 
        'P' AS `pattype`,
        `webmember`.`webmember` AS `webmember`,
        `webmember`.`groupref` AS `groupref`,
        webmember.title as title,
        `webmember`.`fname` AS `fname`,
        `webmember`.`lname` AS `lname`,
        `webmember`.`cell` AS `cell`,
        `webmember`.`webdob` AS `dob`,
        `webmember`.`email` AS `email`,
        `webmember`.`status` AS `status`,
        `webmember`.`webenrolldate` AS `webenrolldate`,
        `webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,
        `webmember`.`is_active` AS `is_active`,
        `webmember`.`provider` AS `providerid`,
        `webmember`.`company` AS `companyid`,
        `provider`.`provider` AS `provider`,
        `company`.`company` AS `company`
    FROM
        ((`webmember`
        LEFT JOIN `company` ON ((`webmember`.`company` = `company`.`id`)))
        LEFT JOIN `provider` ON ((`webmember`.`provider` = `provider`.`id`))) 
    UNION SELECT 
        'D' AS `pattype`,
        `webmember`.`webmember` AS `webmember`,
        `webmember`.`groupref` AS `groupref`,
        webmemberdependants.title as title,
        `webmemberdependants`.`fname` AS `fname`,
        `webmemberdependants`.`lname` AS `lname`,
        `webmember`.`cell` AS `cell`,
        `webmemberdependants`.`depdob` AS `dob`,
        `webmember`.`email` AS `email`,
        `webmember`.`status` AS `status`,
        `webmember`.`webenrolldate` AS `webenrolldate`,
        `webmember`.`webenrollcompletedate` AS `webenrollcompletedate`,
        `webmember`.`is_active` AS `is_active`,
        `webmember`.`provider` AS `providerid`,
        `webmember`.`company` AS `companyid`,
        `provider`.`provider` AS `provider`,
        `company`.`company` AS `company`
    FROM
        (((`webmemberdependants`
        LEFT JOIN `webmember` ON ((`webmemberdependants`.`webmember` = `webmember`.`id`)))
        LEFT JOIN `company` ON ((`company`.`id` = `webmember`.`company`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `webmember`.`provider`)));
USE `prod_dup`;

XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
         treatmentplan.pattitle as title,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
    ORDER BY `treatment`.`id` DESC;


XXXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `newpatient` CHAR(1) NULL DEFAULT NULL AFTER `cell`;

XXXXALTER TABLE `prod_dup`.`t_appointment` 
CHANGE COLUMN `block` `blockappt` CHAR(1) NULL DEFAULT NULL ;

XXX No Longer needed Data of toothcolor table to be imported into PROD DB  (Not required_)

XXXPopulate tooth procedures - Cavit, 19 filling procedures


XXXXUSE `prod_dup`;
CREATE 

XXXXVIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        DATE_FORMAT(`t_appointment`.`f_start_time`,'%d/%m/%Y %H:%i') AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE()));
XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_today` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        DATE_FORMAT(`t_appointment`.`f_start_time`,'%d/%m/%Y %H:%i') AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (CAST(`t_appointment`.`f_start_time` AS DATE) = CURDATE());


XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_weekly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        DATE_FORMAT(`t_appointment`.`f_start_time`,
                '%d/%m/%Y %H:%i') AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (WEEK(`t_appointment`.`f_start_time`, 0) = WEEK(CURDATE(), 0));


03/04/2018 - Added FonePaise properties
========================================

XXXURLPROPERTIES is modified

XXXCREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_fonepaise` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`id` AS `paymentid`,
        `payment`.`amount` AS `invoiceamt`,
        `treatment`.`treatment` AS `invoice`,
        `patientmember`.`cell` AS `mobileno`,
        `patientmember`.`email` AS `email`
    FROM
        ((`payment`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `payment`.`patientmember`)))



03/07/2018
===========

XXXALTER TABLE .`payment` 
ADD COLUMN `fp_status` CHAR(1) NULL AFTER `paymentcommit`,
ADD COLUMN `fp_paymentref` VARCHAR(45) NULL AFTER `fp_status`,
ADD COLUMN `fp_paymenttype` VARCHAR(45) NULL AFTER `fp_paymentref`,
ADD COLUMN `fp_paymentdate` DATE NULL AFTER `fp_paymenttype`,
ADD COLUMN `fp_paymentdetail` VARCHAR(512) NULL AFTER `fp_paymentdate`,
ADD COLUMN `fp_cardtype` VARCHAR(45) NULL AFTER `fp_paymentdetail`,
ADD COLUMN `fp_merchantid` VARCHAR(45) NULL AFTER `fp_cardtype`,
ADD COLUMN `fp_merchantdisplay` VARCHAR(45) NULL AFTER `fp_merchantid`,
ADD COLUMN `fp_invoice` VARCHAR(45) NULL AFTER `fp_merchantdisplay`,
ADD COLUMN `fp_invoiceamt` VARCHAR(45) NULL AFTER `fp_invoice`,
ADD COLUMN `fp_amount` VARCHAR(45) NULL AFTER `fp_invoiceamt`,
ADD COLUMN `fp_fee` VARCHAR(45) NULL AFTER `fp_amount`,
ADD COLUMN `fp_error` VARCHAR(45) NULL AFTER `fp_fee`,
ADD COLUMN `fp_errormsg` VARCHAR(45) NULL AFTER `fp_error`,
ADD COLUMN `fp_otherinfo` VARCHAR(45) NULL AFTER `fp_errormsg`;

XXXALTER TABLE `payment` 
CHANGE COLUMN `fp_invoiceamt` `fp_invoiceamt` DOUBLE NULL DEFAULT NULL ,
CHANGE COLUMN `fp_amount` `fp_amount` DOUBLE NULL DEFAULT NULL ,
CHANGE COLUMN `fp_fee` `fp_fee` DOUBLE NULL DEFAULT NULL ;


XXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_fonepaise` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`id` AS `paymentid`,
        `payment`.`amount` AS `invoiceamt`,
        `provider`.`title` AS `provtitle`,
        `provider`.`providername` AS `providername`,
        `provider`.`practicename` AS `practicename`,
        `treatment`.`treatment` AS `invoice`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`description` AS `description`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `vw_memberpatientlist`.`title` AS `title`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`cell` AS `mobileno`,
        `vw_memberpatientlist`.`email` AS `email`,
        `doctor`.`title` AS `doctortitle`,
        `doctor`.`name` AS `doctorname`
    FROM
        (((((`payment`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `payment`.`treatmentplan`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `treatment`.`doctor`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `payment`.`provider`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `vw_memberpatientlist` ON ((`vw_memberpatientlist`.`patientid` = `payment`.`patientmember`)));


03/16/2018
==========
XXXXSTG- 1. Add a record in auth_permission to set superadmin group access right.

XXXSTG ALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `registered` CHAR(1) NULL DEFAULT NULL AFTER `registration`;

XXXXSTG - 2. Changed to Provider for Acceptance Agreement
ALTER TABLE `prod_dup`.`provider` 
CHANGE COLUMN `groupregion` `groupregion` INT(11) NULL DEFAULT NULL AFTER `sitekey`,
CHANGE COLUMN `registration` `registration` VARCHAR(128) NULL DEFAULT NULL AFTER `groupregion`,
CHANGE COLUMN `registered` `registered` CHAR(1) NULL DEFAULT 'F' AFTER `registration`,
ADD COLUMN `pa_providername` VARCHAR(255) NULL AFTER `registered`,
ADD COLUMN `pa_dob` DATE NULL AFTER `pa_providername`,
ADD COLUMN `pa_parent` VARCHAR(255) NULL AFTER `pa_dob`,
ADD COLUMN `pa_address` VARCHAR(255) NULL AFTER `pa_parent`,
ADD COLUMN `pa_pan` VARCHAR(45) NULL AFTER `pa_address`,
ADD COLUMN `pa_regno` VARCHAR(45) NULL AFTER `pa_pan`,
ADD COLUMN `pa_date` DATETIME NULL AFTER `pa_regno`,
ADD COLUMN `pa_accepted` CHAR(1) NULL DEFAULT 'F' AFTER `pa_date`,
ADD COLUMN `pa_approved` CHAR(1) NULL DEFAULT 'F' AFTER `pa_accepted`,
ADD COLUMN `pa_approvedby` INT(11) NULL AFTER `pa_approved`,
ADD COLUMN `pa_approvedon` DATETIME NULL AFTER `pa_approvedby`;

XXXSTG- ALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `pa_day` VARCHAR(45) NULL AFTER `pa_approvedon`,
ADD COLUMN `pa_month` VARCHAR(45) NULL AFTER `pa_day`,
ADD COLUMN `pa_location` VARCHAR(45) NULL AFTER `pa_month`;

03/22/2018
==========
1. Modified Provider to add practice address  in mydentalplan
XXXSTG-ALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `p_address1` VARCHAR(45) NULL AFTER `pin`,
ADD COLUMN `p_address2` VARCHAR(45) NULL AFTER `p_address1`,
ADD COLUMN `p_address3` VARCHAR(45) NULL AFTER `p_address2`,
ADD COLUMN `p_city` VARCHAR(45) NULL AFTER `p_address3`,
ADD COLUMN `p_st` VARCHAR(45) NULL AFTER `p_city`,
ADD COLUMN `p_pin` VARCHAR(45) NULL AFTER `p_st`;

2. Vw Fonepaise
XXXXSTG-USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_fonepaise` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`id` AS `paymentid`,
        `payment`.`amount` AS `invoiceamt`,
        `payment`.`notes` AS `notes`,
        `provider`.`id` AS `providerid`,
        `provider`.`title` AS `provtitle`,
        `provider`.`providername` AS `providername`,
        `provider`.`practicename` AS `practicename`,
        `treatment`.`treatment` AS `invoice`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`description` AS `description`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `vw_memberpatientlist`.`title` AS `title`,
        `vw_memberpatientlist`.`patientid` AS `patientid`,
        `vw_memberpatientlist`.`primarypatientid` AS `memberid`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`cell` AS `mobileno`,
        `vw_memberpatientlist`.`email` AS `email`,
        `doctor`.`title` AS `doctortitle`,
        `doctor`.`name` AS `doctorname`
    FROM
        (((((`payment`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `payment`.`treatmentplan`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `treatment`.`doctor`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `payment`.`provider`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `vw_memberpatientlist` ON ((`vw_memberpatientlist`.`patientid` = `payment`.`patientmember`)));

03/26/2018
==========
XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`provider` 
ADD COLUMN `pa_practicename` VARCHAR(128) NULL AFTER `pa_providername`;

XXXALTER TABLE `mydentalplan$my_dentalplan_prod`.`provider` 
ADD COLUMN `pa_pin` VARCHAR(45) NULL AFTER `pa_location`;

XXXALTER TABLE `prod_dup`.`provider` 
ADD COLUMN `pa_practiceaddress` VARCHAR(255) NULL DEFAULT NULL AFTER `pa_practicename`;
ALTER TABLE `prod_dup`.`provider` 
CHANGE COLUMN `pa_pin` `pa_practicepin` VARCHAR(45) NULL DEFAULT NULL ;

03/27/2018
============

1. XXXXAdd Status field to 'Treatment_procedure' table

2. XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`status` AS `status`,
        `treatment_procedure`.`remarks` AS `remarks`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));


XXXXALTER TABLE `prod_dup`.`treatment` 
CHANGE COLUMN `status` `status` VARCHAR(45) NULL DEFAULT NULL ;



XXXALTER TABLE `prod_dup`.`treatment` 
CHANGE COLUMN `quadrant` `quadrant` VARCHAR(45) NULL DEFAULT NULL AFTER `dentalprocedure`,
CHANGE COLUMN `tooth` `tooth` VARCHAR(45) NULL DEFAULT NULL AFTER `quadrant`,
CHANGE COLUMN `chiefcomplaint` `chiefcomplaint` VARCHAR(128) NULL DEFAULT NULL AFTER `tooth`,
ADD COLUMN `authorized` CHAR(1) NULL DEFAULT 'F' AFTER `chiefcomplaint`;

XXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `authorized` CHAR(1) NULL DEFAULT 'F' AFTER `remarks`;

XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`status` AS `status`,
        `treatment_procedure`.`authorized` AS `authorized`,
        `treatment_procedure`.`remarks` AS `remarks`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`
    FROM
        ((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));

XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentplansummary` AS
    SELECT 
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`provider` AS `provider`,
        `treatmentplan`.`is_active` AS `is_active`,
        SUM(`treatmentplan`.`totaltreatmentcost`) AS `totalcost`,
        SUM(treatmentplan.totalcopay) AS totalcopay,
        SUM(treatmentplan.totalinspays) as totalinspays,
        SUM(treatmentplan.totalpaid) as totalpaid,
        SUM(treatmentplan.totaldue) as totaldue,
        SUM(treatmentplan.totalcopaypaid) as totalcopaypaid,
        SUM(treatmentplan.totalinspaid) as totalinspaid
    FROM
        `treatmentplan`
    WHERE
        (`treatmentplan`.`is_active` = 'T')
    GROUP BY `treatmentplan`.`primarypatient` , `treatmentplan`.`provider`;

XXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentsummary1` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`provider` AS `provider`,
        `vw_treatmentplansummary`.`totalcost` AS `totalcost`,
        `vw_treatmentplansummary`.`totalinspays` AS `totalinspays`,
        `vw_treatmentplansummary`.`totalcopay` AS `totalcopay`,
         SUM(`payment`.`amount`) AS `totalpaid`,
         `vw_treatmentplansummary`.`totalcost`  -SUM(`payment`.`amount`) AS `totaldue`
    FROM
        (`payment`
        LEFT JOIN `vw_treatmentplansummary` ON ((`payment`.`patientmember` = `vw_treatmentplansummary`.`memberid`)))
    GROUP BY `payment`.`patientmember`;

XXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_fonepaise` AS
    SELECT 
        `payment`.`id` AS `id`,
        `payment`.`id` AS `paymentid`,
        `payment`.`amount` AS `invoiceamt`,
        `payment`.`notes` AS `notes`,
        `provider`.`id` AS `providerid`,
        `provider`.`title` AS `provtitle`,
        `provider`.`providername` AS `providername`,
        `provider`.`practicename` AS `practicename`,
        treatment.id as treatmentid,
        `treatment`.`treatment` AS `invoice`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`description` AS `description`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        treatmentplan.id as tplanid,
        `vw_memberpatientlist`.`title` AS `title`,
        `vw_memberpatientlist`.`patientid` AS `patientid`,
        `vw_memberpatientlist`.`primarypatientid` AS `memberid`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`cell` AS `mobileno`,
        `vw_memberpatientlist`.`email` AS `email`,
        `doctor`.`title` AS `doctortitle`,
        `doctor`.`name` AS `doctorname`
    FROM
        (((((`payment`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `payment`.`treatmentplan`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `treatment`.`doctor`)))
        LEFT JOIN `provider` ON ((`provider`.`id` = `payment`.`provider`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `vw_memberpatientlist` ON ((`vw_memberpatientlist`.`patientid` = `payment`.`patientmember`)));
	
	
XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_membertreatmentplans_detail_rpt` AS
    SELECT 
       `treatmentplan`.`id` AS `id`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`status` AS `status`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`enddate` AS `enddate`,
        `treatment`.`quadrant` AS `quadrant`,
        `treatment`.`tooth` AS `tooth`,
        `treatment`.`description` AS `description`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`actualtreatmentcost` AS `actualtreatmentcost`,
        `treatment`.`copay` AS `copay`,
        `treatment`.`inspay` AS `inspay`,
        
        provider.providername as providername,
        provider.practicename as practicename,
        provider.cell as providercell,
        provider.email as provideremail,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        `treatmentplan`
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`) & (`treatment`.`is_active` = 'T'))
        LEFT JOIN `vw_memberpatientlist` ON (((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T'))
        LEFT JOIN  provider on provider.id = treatmentplan.provider
    ORDER BY `treatmentplan`.`id`;
	


XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_provider` AS
    SELECT 
		id as id,
        `provider`.`id` AS `providerid`,
        CONCAT(`provider`.`providername`,
                ' :',
                `provider`.`provider`) AS `provider`
    FROM
        `provider`;


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentpaymentreport` AS
    SELECT 
        
        `treatmentplan`.`id` AS `id`,
        treatment.treatment AS treatment,
        treatment.id as treatmentid,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`provider` AS `providerid`,
        SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`treatmentplan`.`totalcopay`, 0)) AS `totalcopay`,
        SUM(IFNULL(`treatmentplan`.`totalinspays`, 0)) AS `totalinspays`,
        ((SUM(IFNULL(`treatmentplan`.`totaltreatmentcost`, 0)) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) - SUM(IFNULL(`treatmentplan`.`totalinspays`, 0))) AS `totalmemberpays`,
        SUM(IFNULL(`treatmentplan`.`totalpaid`, 0)) AS `totalpaid`,
        SUM(IFNULL(`treatmentplan`.`totalcopaypaid`, 0)) AS `totalcopaypaid`,
        SUM(IFNULL(`treatmentplan`.`totalinspaid`, 0)) AS `totalinspaid`,
        SUM(IFNULL(`treatmentplan`.`totaldue`, 0)) AS `totaldue`,
        `vw_memberpatientlist`.`email` AS `memberemail`,
        `vw_memberpatientlist`.`cell` AS `membercell`,
        CONCAT(`vw_memberpatientlist`.`fname`,
                ' ',
                `vw_memberpatientlist`.`lname`,
                ' (',
                `vw_memberpatientlist`.`patientmember`,
                ')') AS `membername`,
        CONCAT(`vw_memberpatientlist`.`cell`,
                '-',
                `vw_memberpatientlist`.`email`) AS `membercontact`,
        CONCAT(`patientmember`.`address1`,
                ' ',
                `patientmember`.`address2`,
                ' ',
                `patientmember`.`city`,
                ' ',
                `patientmember`.`st`,
                ' ',
                `patientmember`.`pin`) AS `memberaddress`,
        `provider`.`providername` AS `providername`,
        CONCAT(`provider`.`address1`,
                ' ',
                `provider`.`address2`,
                ' ',
                `provider`.`city`,
                ' ',
                `provider`.`st`,
                ' ',
                `provider`.`pin`) AS `provaddress`,
        CONCAT(`provider`.`cell`,
                '-',
                `provider`.`email`) AS `provcontact`,
        CONCAT(`company`.`name`,
                ' (',
                `company`.`company`,
                ')') AS `company`,
        CONCAT(`hmoplan`.`name`,
                ' (',
                `hmoplan`.`hmoplancode`,
                ')') AS `hmoplan`,
        `vw_memberpatientlist`.`premenddt` AS `premenddt`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        (((((`treatmentplan`
        LEFT JOIN `vw_memberpatientlist` ON ((((`treatmentplan`.`primarypatient` = `vw_memberpatientlist`.`primarypatientid`) & (`treatmentplan`.`patient` = `vw_memberpatientlist`.`patientid`)) & (`vw_memberpatientlist`.`is_active` = 'T'))))
        LEFT JOIN `provider` ON ((`treatmentplan`.`provider` = `provider`.`id`)))
        LEFT JOIN `company` ON ((`vw_memberpatientlist`.`company` = `company`.`id`)))
        LEFT JOIN `hmoplan` ON ((`vw_memberpatientlist`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`treatmentplan`.`primarypatient` = `patientmember`.`id`)))
        LEFT JOIN treatment ON ((treatment.treatmentplan = treatmentplan.id))
    GROUP BY `treatmentplan`.`primarypatient` , `treatmentplan`.`treatmentplan`, treatment.treatment;

03/31/2018
==========
XXImport ProcedurePricePlan

XXXCREATE TABLE `prod_dup`.`importprocedurepriceplan` (
  `id` INT(11) NOT NULL,
  `priceplancode` VARCHAR(45) NULL,
  `procedurecode` VARCHAR(45) NULL,
  `proceduredescription` VARCHAR(255) NULL,
  `UCR` VARCHAR(45) NULL,
  `CoPay` VARCHAR(45) NULL,
  is_free char(1),
  `Remarks` VARCHAR(45) NULL,
  PRIMARY KEY (`id`));

XXinsert into procedurepriceplan (providerid, procedurepriceplancode, procedurecode, ucrfee, procedurefee,copay, companypays,inspays,remarks,is_free,is_active, created_by,created_on, modified_by, modified_on)
select 0, priceplancode,procedurecode,ucr,0,copay,0,0,remarks,is_free,'T',1,NOW(),1,NOW() FROM importprocedurepriceplan

XXXUPDATE dentalprocedure AS DP1, importprocedurepriceplan AS DP2 
SET DP1.shortdescription = dp2.proceduredescription
WHERE DP1.dentalprocedure = DP2.procedurecode


XXXinsert into dentalprocedure (dentalprocedure, category, shortdescription,description, procedurefee, for_chart,chartcolor,is_free,is_active,created_on,created_by,modified_on, modified_by)
select A.procedurecode, 'G', A.proceduredescription, A.proceduredescription, 0,'F','#000000','F','T',NOW(),1,NOW(),1 from 
(select importprocedurepriceplan.procedurecode ,importprocedurepriceplan.proceduredescription , dentalprocedure.dentalprocedure from importprocedurepriceplan
left join dentalprocedure on dentalprocedure.dentalprocedure = importprocedurepriceplan.procedurecode) AS A
WHERE A.dentalprocedure IS NULL


update procedurepriceplan set procedurepriceplancode = CONCAT('x', procedurepriceplancode), procedurecode = CONCAT('x',procedurecode), is_active  = 'F'  where procedurepriceplancode = 'I103'
update dentalprocedure set dentalprocedure = concat('x', dentalprocedure), is_active = 'F' 

insert into dentalprocedure (dentalprocedure, category, shortdescription, description, procedurefee,for_chart, chartcolor, remarks,is_free,is_active, created_by,created_on, modified_by, modified_on)
select procedurecode, LEFT(procedurecode,1),proceduredescription, proceduredescription,0,'F', NULL,remarks,is_free,'T',1,NOW(),1,NOW() FROM importprocedurepriceplan

insert into procedurepriceplan (providerid, procedurepriceplancode, procedurecode, ucrfee, procedurefee,copay, companypays,inspays,remarks,is_free,is_active, created_by,created_on, modified_by, modified_on)
select 0, priceplancode,procedurecode,ucr,0,copay,0,0,remarks,is_free,'T',1,NOW(),1,NOW() FROM importprocedurepriceplan


04/01/2018
==========
1. Change vw_casereport - primarypatientid

04/19/2018
===========
1. 
XXXAdded 2 fields - medi_percent, mdp_medi_percent fields in URLPropertis

2.
XXXALTER TABLE `prod_dup`.`treatment` 
ADD COLUMN `medi_deductions` DOUBLE NULL DEFAULT 0 AFTER `companypay`,
ADD COLUMN `mdp_medi_deductions` DOUBLE NULL DEFAULT 0 AFTER `medi_deductions`;

3.
XXXXALTER TABLE `prod_dup`.`urlproperties` 
CHANGE COLUMN `mdp_medi_percent` `medi_mydp_percent` DOUBLE NULL DEFAULT '15' ,
ADD COLUMN `medi_email` VARCHAR(255) NULL AFTER `medi_mydp_percent`,
ADD COLUMN `medi_mydp_email` VARCHAR(255) NULL AFTER `medi_email`;

XXXXALTER TABLE `prod_dup`.`urlproperties` 
CHANGE COLUMN `medi_percent` `medi_percent` DOUBLE NULL DEFAULT '5' ,
CHANGE COLUMN `medi_mydp_percent` `medi_mydp_percent` DOUBLE NULL DEFAULT '15' ;

4.
Make changes to status.py and treatmentstatus.py

5.
XXXALTER TABLE `prod_dup`.`auth_user` 
ADD COLUMN `impersonated` CHAR(1) NULL DEFAULT 'F' AFTER `registration_id`,
ADD COLUMN `impersonatorid` INT(11) NULL DEFAULT 1 AFTER `impersonated`,
ADD COLUMN `impersonatorfname` VARCHAR(255) NULL DEFAULT NULL AFTER `impersonatorid`,
ADD COLUMN `impersonatorlname` VARCHAR(255) NULL DEFAULT NULL AFTER `impersonatorfname`;

6.
XXXALTER TABLE `prod_dup`.`company` 
CHANGE COLUMN `maxsubscribers` `maxsubscribers` INT(11) ZEROFILL NULL DEFAULT '4' ,
ADD COLUMN `authorization` CHAR(1) NULL DEFAULT 'F' AFTER `dependantmode`;
ALTER TABLE `prod_dup`.`company` 
CHANGE COLUMN `authorization` `authorizationrequired` CHAR(1) NULL DEFAULT 'F' ;

4/29/2018
=========
USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_today` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        doctor.id as doctorid,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (CAST(`t_appointment`.`f_start_time` AS DATE) = CURDATE());


USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_weekly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
		`doctor`.`id` AS `doctorid`,        
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (WEEK(`t_appointment`.`f_start_time`, 0) = WEEK(CURDATE(), 0));

USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        doctor.id as doctorid,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
    WHERE
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE()));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_today` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
	 `vw_treatmentlist`.`patientid` AS `patientid`,
      `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
        (CAST(`t_appointment`.`f_start_time` AS DATE) = CURDATE());


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_weekly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
 `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,      
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
          LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`))
    WHERE
        (WEEK(`t_appointment`.`f_start_time`, 0) = WEEK(CURDATE(), 0));

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        (`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
         LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`))
    WHERE
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE()));


XXXALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `f_status` VARCHAR(45) NULL DEFAULT NULL AFTER `f_treatmentid`;

USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE()));

USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_today` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        t_appointment.f_status AS f_status,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
        (CAST(`t_appointment`.`f_start_time` AS DATE) = CURDATE());


USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_weekly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        t_appointment.f_status as f_status,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
        (WEEK(`t_appointment`.`f_start_time`, 0) = WEEK(CURDATE(), 0));


USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        'T' AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `modified_on` desc;

5/27/2018
==========
USE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                patientmember.email ) AS `pattern`,        
                
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
		CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                patientmember.email ) AS `pattern`,         
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        'T' AS `hmoplanname`,
        'T' AS `hmoplancode`,
        'T' AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
    ORDER BY `id` DESC;


05/31/2018
==========
USE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'P' AS `patienttype`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                `patientmember`.`email`) AS `pattern`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                `patientmember`.`email`) AS `pattern`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        (`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
	ORDER BY `ID` DESC;

6/6/2018
========
XXXCREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymenttotalpaid` AS
    SELECT 
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`treatmentplan` AS `treatmentplan`,
        `payment`.`provider` AS `provider`,
        SUM(`payment`.`amount`) AS `totalpaid`
    FROM
        `payment`
    GROUP BY `payment`.`treatmentplan`
    
XXXXCREATE VIEW vw_treatmentplansummarybytreatment AS

SELECT 
        treatmentplan.id,
        `treatmentplan`.`provider` AS `provider`,
        `treatmentplan`.`is_active` AS `is_active`,
        SUM(`treatmentplan`.`totaltreatmentcost`) AS `totalcost`,
        SUM(`treatmentplan`.`totalcopay`) AS `totalcopay`,
        SUM(`treatmentplan`.`totalinspays`) AS `totalinspays`,
        vw_paymenttotalpaid.totalpaid as totalpaid,
        SUM(`treatmentplan`.`totaltreatmentcost`) - SUM(`treatmentplan`.`totalinspays`)  - vw_paymenttotalpaid.totalpaid as totaldue,
        SUM(`treatmentplan`.`totalcopaypaid`) AS `totalcopaypaid`,
        SUM(`treatmentplan`.`totalinspaid`) AS `totalinspaid`
    FROM
        `treatmentplan`
	left join vw_paymenttotalpaid on vw_paymenttotalpaid.treatmentplan = treatmentplan.id
    WHERE
        (`treatmentplan`.`is_active` = 'T')
    GROUP BY `treatmentplan`.`id` 

6/10/2018

XXXXvw_paymentlist

XXXvw_treatmentplansummarybypatient
XXXXvw_payment_treatmentplan_treatment


12-Jul_2018
===========
1. XXXXXmodified vw_patientprescription
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_patientprescription` AS
    SELECT 
        `prescription`.`id` AS `id`,
        `prescription`.`providerid` AS `providerid`,
        `prescription`.`tplanid` AS `tplanid`,
        `prescription`.`treatmentid` AS `treatmentid`,
        `prescription`.`dosage` AS `dosage`,
        `prescription`.`frequency` AS `frequency`,
        `prescription`.`quantity` AS `quantity`,
        `prescription`.`remarks` AS `remarks`,
        `prescription`.`prescriptiondate` AS `prescriptiondate`,
        `medicine`.`id` AS `medicineid`,
        `medicine`.`medicine` AS `medicine`,
        `medicine`.`medicinetype` AS `medicinetype`,
        `medicine`.`strength` AS `strength`,
        `medicine`.`strengthuom` AS `strengthuom`,
        `medicine`.`instructions` AS `instructions`,
        `prescription`.`patientid` AS `patientid`,
        `prescription`.`memberid` AS `memberid`,
        `vw_memberpatientlist`.`title` AS `title`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `vw_memberpatientlist`.`dob` AS `dob`,
        (YEAR(NOW()) - YEAR(`vw_memberpatientlist`.`dob`)) AS `age`,
        `vw_memberpatientlist`.`gender` AS `gender`,
        `doctor`.`id` AS `doctorid`,
        `doctor`.`title` AS `doctitle`,
        `doctor`.`name` AS `doctorname`,
        `prescription`.`is_active` AS `is_active`
    FROM
        (((`prescription`
        LEFT JOIN `medicine` ON (((`medicine`.`id` = `prescription`.`medicineid`)
            AND (`prescription`.`providerid` = `medicine`.`providerid`)
            AND (`prescription`.`is_active` = 'T'))))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`providerid` = `prescription`.`providerid`)
            AND (`vw_memberpatientlist`.`patientid` = `prescription`.`patientid`)
            AND (`vw_memberpatientlist`.`primarypatientid` = `prescription`.`memberid`))))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `prescription`.`doctorid`)))
	
2. XXXvw_memberpatientlist
XXXXUSE `prod_dup`;
XXXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'P' AS `patienttype`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`) AS `fullname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                `patientmember`.`email`) AS `pattern`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        'Self' AS `relation`,
        `patientmember`.`image` AS `image`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmember`.`dob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                `patientmember`.`email`) AS `pattern`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmemberdependants`.`relation` AS `relation`,
        'T' AS `image`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        (YEAR(NOW()) - YEAR(`patientmemberdependants`.`depdob`)) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
    ORDER BY `ID` DESC;

07/16/2018
===========
1. xxxAdded uniqueid field in t_appointment
ALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `f_uniqueid` INT(11) NULL DEFAULT NULL AFTER `id`;

2. XXXXNeed to change failure call backurl in urlproperties. it is to be set to callbacurl on success

07/21/2018
=========
xxx1. added treatmentid in casereport
ALTER TABLE `prod_dup`.`casereport` 
ADD COLUMN `treatmentid` INT(11) NULL DEFAULT NULL AFTER `doctorid`;

ALTER TABLE `prod_dup`.`casereport` 
ADD COLUMN `appointmentid` INT(11) NULL AFTER `treatmentid`;


xxxx2. added treatmentid and appointmentid in vw_casereport
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_casereport` AS
    SELECT 
        `casereport`.`id` AS `id`,
        `casereport`.`providerid` AS `providerid`,
        `casereport`.`patientid` AS `patientid`,
        `casereport`.`treatmentid` AS `treatmentid`,
        `casereport`.`appointmentid` AS `appointmentid`,
        `casereport`.`casereport` AS `casereport`,
        `doctor`.`name` AS `doctorname`,
        `provider`.`providername` AS `providername`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `casereport`.`is_active` AS `is_active`,
        `casereport`.`modified_on` AS `modified_on`,
        `casereport`.`modified_by` AS `modified_by`
    FROM
        (((`casereport`
        LEFT JOIN `doctor` ON ((`casereport`.`doctorid` = `doctor`.`id`)))
        LEFT JOIN `provider` ON ((`casereport`.`providerid` = `provider`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON ((`casereport`.`patientid` = `vw_memberpatientlist`.`primarypatientid`)));

07/23/2018
==========

1. XXaltered vw_treatmentprocedure  added treatmentid
2. XXXaltered vw_membertreatmentplans_detail_rpt added treatmentid

07/25/2018
===========

1. XXXImportMember - change width to 128
ALTER TABLE `prod_dup`.`importmember` 
CHANGE COLUMN `address1` `address1` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `address2` `address2` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `address3` `address3` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `provaddr1` `provaddr1` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `provaddr2` `provaddr2` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `provaddr3` `provaddr3` VARCHAR(128) NULL DEFAULT NULL ;

2. XXXXProvider - change width to 128
ALTER TABLE `prod_dup`.`provider` 
CHANGE COLUMN `address1` `address1` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `address2` `address2` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `address3` `address3` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address1` `p_address1` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address2` `p_address2` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address3` `p_address3` VARCHAR(128) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_location` `pa_location` VARCHAR(128) NULL DEFAULT NULL ;


XXXXALTER TABLE `prod_dup`.`importmember` 
CHANGE COLUMN `st` `st` VARCHAR(50) NULL DEFAULT NULL AFTER `paymentdate`;


change telehone to telephone


07/28/2018
===========
XXXALTER TABLE `prod_dup`.`payment` 
ADD COLUMN `chequeno` VARCHAR(45) NULL AFTER `modified_by`,
ADD COLUMN `bankname` VARCHAR(128) NULL AFTER `checqueno`,
ADD COLUMN `accountname` VARCHAR(128) NULL AFTER `bankname`,
ADD COLUMN `accountno` VARCHAR(45) NULL AFTER `accountname`;


8/1/2018
========
UPDATE webmember pm, importtemp impt
SET pm.webdob = impt.dob, pm.webenrolldate = impt.enroldate, 
pm.webenrollcompletedate = impt.enroldate, pm.startdate = impt.premstartdt
where pm.webmember = impt.patientmember


8/3/2018
=========

1.XXXX Added sendsms flag in t_appt table
ALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `sendsms` CHAR(1) NULL DEFAULT 'F' AFTER `blockappt`;

2.XXXX created view vw_appointments
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointments` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_uniqueid` AS `f_uniqueid`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`ptitle` AS `ptitle`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_end_time` AS `f_end_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_location` AS `f_location`,
        `t_appointment`.`f_treatmentid` AS `f_treatmentid`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `provider`,
        `t_appointment`.`doctor` AS `doctor`,
        `t_appointment`.`color` AS `color`,
        `t_appointment`.`patientmember` AS `patientmember`,
        `t_appointment`.`patient` AS `patient`,
        `t_appointment`.`cell` AS `cell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        `t_appointment`.`blockappt` AS `blockappt`,
        `t_appointment`.`sendsms` AS `sendsms`,
        `t_appointment`.`is_active` AS `is_active`,
        `t_appointment`.`created_on` AS `created_on`,
        `t_appointment`.`created_by` AS `created_by`,
        `t_appointment`.`modified_on` AS `modified_on`,
        `t_appointment`.`modified_by` AS `modified_by`,
        `doctor`.`name` AS `docname`,
        `doctor`.`cell` AS `doccell`,
        `doctor`.`email` AS `docemail`,
        `provider`.`cell` AS `provcell`,
        provider.providername as provname,
        provider.email as provemail,
        `provider`.`practicename` AS `clinic`
    FROM
        ((`t_appointment`
        LEFT JOIN `provider` ON ((`provider`.`id` = `t_appointment`.`provider`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)));


8/6/2018
=========
1.XXXX Modified vw_treatmentlist

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`pattitle` AS `title`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`,
        CONCAT(`treatmentplan`.`patientname`,
                ':',
                `treatment`.`treatment`) AS `pattreatment`,
                
        CONCAT(`treatmentplan`.`patientname`,
                ' ',
                `treatment`.`treatment`) AS `pattern`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
    ORDER BY `treatment`.`id` DESC;

2. URL Properties medi_mydp_cell col. added
============================================
XXXXALTER TABLE `prod_dup`.`urlproperties` 
ADD COLUMN `medi_mydp_cell` VARCHAR(45) NULL AFTER `medi_mydp_email`;


8/7/2018
========
1.XXXX Creating new view
Create view vw_treatment_procedure_group AS
SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
         treatment_procedure.dentalprocedure as procedureid,
         group_concat(dentalprocedure.shortdescription separator ';')  as shortdescription
    FROM
        `treatment_procedure`
         LEFT JOIN `treatment` ON (`treatment`.`id` = `treatment_procedure`.`treatmentid`)
         LEFT JOIN dentalprocedure on dentalprocedure.id = treatment_procedure.dentalprocedure
         WHERE treatment_procedure.is_active = 'T'
         group by treatmentid
	 
2. XXXXvw_paymentgroup
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentgroup` AS
    SELECT 
       
	   `payment`.`treatmentplan` AS `id`,
        MAX(`payment`.`paymentdate`) AS `lastpaymentdate`,
        COUNT(`payment`.`id`) AS `paymentscount`,
        `payment`.`amount` AS `amount`
    FROM
        `payment`
    GROUP BY `payment`.`treatmentplan`
    ORDER BY `payment`.`paymentdate` DESC;

3. XXXXXcreate view vw_payments

  USE `prod_dup`;
CREATE 
 
 OR REPLACE VIEW `prod_dup`.`vw_payments` AS
    SELECT 
        `prod_dup`.`treatmentplan`.`id` AS `id`,
        `prod_dup`.`treatment`.`treatment` AS `treatment`,
        `prod_dup`.`treatment`.`id` AS `treatmentid`,
        `prod_dup`.`treatment`.`startdate` AS `treatmentdate`,
        `vw_treatment_procedure_group`.`shortdescription` AS `shortdescription`,
        `prod_dup`.`treatmentplan`.`primarypatient` AS `memberid`,
        `prod_dup`.`treatmentplan`.`patient` AS `patientid`,
        `prod_dup`.`treatmentplan`.`provider` AS `providerid`,
        `vw_memberpatientlist`.`fullname` AS `patientname`,
        `vw_paymentgroup`.`paymentscount` AS `paymentscount`,
        `vw_paymentgroup`.`amount` AS `lastpayment`,
        `vw_paymentgroup`.`lastpaymentdate` AS `lastpaymentdate`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totaltreatmentcost`,
                0)) AS `totaltreatmentcost`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalcopay`,
                0)) AS `totalcopay`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalinspays`,
                0)) AS `totalinspays`,
        ((SUM(IFNULL(`prod_dup`.`treatmentplan`.`totaltreatmentcost`,
                0)) - SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalinspays`,
                0))) - SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalinspays`,
                0))) AS `totalmemberpays`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalpaid`,
                0)) AS `totalpaid`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalcopaypaid`,
                0)) AS `totalcopaypaid`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totalinspaid`,
                0)) AS `totalinspaid`,
        SUM(IFNULL(`prod_dup`.`treatmentplan`.`totaldue`, 0)) AS `totaldue`,
        `prod_dup`.`treatmentplan`.`is_active` AS `is_active`
    FROM
        ((((`prod_dup`.`treatmentplan`
        LEFT JOIN `prod_dup`.`treatment` ON ((`prod_dup`.`treatment`.`treatmentplan` = `prod_dup`.`treatmentplan`.`id`)))
        LEFT JOIN `prod_dup`.`vw_treatment_procedure_group` ON ((`vw_treatment_procedure_group`.`treatmentid` = `prod_dup`.`treatment`.`id`)))
        LEFT JOIN `prod_dup`.`vw_memberpatientlist` ON (((`vw_memberpatientlist`.`primarypatientid` = `prod_dup`.`treatmentplan`.`primarypatient`)
            AND (`vw_memberpatientlist`.`patientid` = `prod_dup`.`treatmentplan`.`patient`))))
        LEFT JOIN `prod_dup`.`vw_paymentgroup` ON ((`vw_paymentgroup`.`id` = `prod_dup`.`treatmentplan`.`id`)))
    GROUP BY `prod_dup`.`treatment`.`id` DESC , `prod_dup`.`treatment`.`startdate` DESC;

4. XXXXXaltered vw_paymentlist
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymentlist` AS
    SELECT 
        `payment`.`id` AS `id`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `payment`.`paymentdate` AS `paymentdate`,
        `payment`.`amount` AS `amount`,
        `payment`.`paymenttype` AS `paymenttype`,
        `payment`.`paymentmode` AS `paymentmode`,
        `payment`.`payor` AS `payor`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `patientmember`.`title` AS `title`,
        `treatmentplan`.`patientname` AS `patientname`,
        CONCAT(`patientmember`.`fname`,
                ' ',
                `patientmember`.`lname`,
                ' (',
                `patientmember`.`patientmember`,
                ')') AS `patientmember`,
        `treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `treatmentplan`.`totalcopay` AS `totalcopay`,
        `treatmentplan`.`totalinspays` AS `totalinspays`,
        `treatmentplan`.`totalpaid` AS `totalpaid`,
        `treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,
        `treatmentplan`.`totalinspaid` AS `totalinspaid`,
        `treatmentplan`.`totaldue` AS `totaldue`,
        `payment`.`is_active` AS `is_active`,
        `payment`.`paymentcommit` AS `paymentcommit`,
        `payment`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`id` AS `treatmentid`,
        payment.fp_status AS fppaymentstatus,
        payment.fp_paymentref AS fppaymentref,
        payment.fp_paymenttype AS fppaymenttype,
        payment.fp_paymentdetail as fppaymentdetail,
        payment.fp_cardtype as fppaymentcard
    FROM
        (((`payment`
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `payment`.`treatmentplan`)))
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `payment`.`patientmember`)));

08/12/2018
==========
1. XXXXURLProperties 
added 6 flags


08/28/2018
=========

XXXXvw_patientmemberbirthday

09/01/2018
===========
XXXXTBALE casereport - added memberid

XXXvw_casereport
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_casereport` AS
    SELECT 
        `casereport`.`id` AS `id`,
        `casereport`.`providerid` AS `providerid`,
        casereport.memberid as memberid,
        `casereport`.`patientid` AS `patientid`,
        `casereport`.`treatmentid` AS `treatmentid`,
        `casereport`.`appointmentid` AS `appointmentid`,
        `casereport`.`casereport` AS `casereport`,
        `doctor`.`name` AS `doctorname`,
        `provider`.`providername` AS `providername`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `casereport`.`is_active` AS `is_active`,
        `casereport`.`modified_on` AS `modified_on`,
        `casereport`.`modified_by` AS `modified_by`
    FROM
        (((`casereport`
        LEFT JOIN `doctor` ON ((`casereport`.`doctorid` = `doctor`.`id`)))
        LEFT JOIN `provider` ON ((`casereport`.`providerid` = `provider`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON (((`casereport`.`memberid` = `vw_memberpatientlist`.`primarypatientid`) AND (`casereport`.`patientid` = `vw_memberpatientlist`.`patientid`))));


06/09/2018
==========
1. XXXXcreated activitytracker table
CREATE TABLE `prod_dup`.`activitytracker` (
  `id` INT(11) NOT NULL,
  `memberid` INT(11) NULL,
  `patientid` INT(11) NULL,
  `appointmentid` INT(11) NULL,
  `treatmentid` INT(11) NULL,
  `paymentid` INT(11) NULL,
  `providerid` VARCHAR(45) NULL,
  `doctorid` VARCHAR(45) NULL,
  `providername` VARCHAR(45) NULL,
  `doctorname` VARCHAR(45) NULL,
  `patientmember` VARCHAR(45) NULL,
  `patientname` VARCHAR(128) NULL,
  `appointmentdate` DATETIME NULL,
  `appointmentstatus` VARCHAR(45) NULL,
  `lastapptactivity` DATETIME NULL,
  `treatment` VARCHAR(45) NULL,
  `procedures` VARCHAR(255) NULL,
  `treatmentcost` DOUBLE NULL,
  `lasttreatmentactivity` DATETIME NULL,
  `paymentdate` DATETIME NULL,
  `paymentmode` VARCHAR(45) NULL,
  `paymentamount` VARCHAR(45) NULL,
  `totalcost` DOUBLE NULL,
  `totalpaid` DOUBLE NULL,
  `totaldue` DOUBLE NULL,
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));

ALTER TABLE `prod_dup`.`activitytracker` 
CHANGE COLUMN `memberid` `memberid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `patientid` `patientid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `appointmentid` `appointmentid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `treatmentid` `treatmentid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `paymentid` `paymentid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `providerid` `providerid` INT(11) NULL DEFAULT 0 ,
CHANGE COLUMN `doctorid` `doctorid` INT(11) NULL DEFAULT 0 ;


2. XXXXvw_treatmentlist

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentlist` AS
    SELECT 
        `treatment`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`chiefcomplaint` AS `chiefcomplaint`,
        `treatment`.`startdate` AS `startdate`,
        `treatment`.`status` AS `status`,
        `treatment`.`treatmentcost` AS `treatmentcost`,
        `treatment`.`is_active` AS `is_active`,
        treatment.modified_on AS modified_on,
        `vw_procedurepriceplan`.`procedurecode` AS `dentalprocedure`,
        `vw_procedurepriceplan`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`id` AS `tplanid`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`pattitle` AS `title`,
        `treatmentplan`.`patientname` AS `patientname`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`,
        CONCAT(`treatmentplan`.`patientname`,
                ':',
                `treatment`.`treatment`) AS `pattreatment`,
        CONCAT(`treatmentplan`.`patientname`,
                ' ',
                `treatment`.`treatment`) AS `pattern`
    FROM
        ((`treatment`
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment`.`dentalprocedure`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
    ORDER BY `treatment`.`id` DESC;


09/22/2018
==========
1.XXXCREATE TABLE `providercount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providercount` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=327 DEFAULT CHARSET=utf8;


09/24/2018
==========
1. XXXXURLPROPERTIES
ALTER TABLE `prod_dup`.`urlproperties` 
ADD COLUMN `timeinterval` DOUBLE NULL DEFAULT 0 AFTER `groupemail`;


09/29/2018
===========
1. XXXXvw_treatmentlist

Added doctorid, doctorname 


2. XXXXCREATE TABLE `prod_dup`.`groupsmscount` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `smsdate` DATE NULL DEFAULT NULL,
  `smscount` INT(11) NULL DEFAULT 0,
  PRIMARY KEY (`id`));


10/02/2018
===========
1. XXXvw_procedurepriceplan
2. XXXw_procedurepriceplan_x999
3. XXXvw_treatment_procedure_group

10/09/2018
==========
XXXALTER TABLE preregister` 
XXXADD COLUMN `address` LONGTEXT NULL AFTER `lname`,
XXXXADD COLUMN `city` VARCHAR(45) NULL AFTER `address`,
XXXADD COLUMN `pii` VARCHAR(45) NULL AFTER `city`;

10/10/2018
============
1. XXXXcreate view vw_doctor
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_doctor` AS select `dr`.`title` AS `doctortitle`,`dr`.`name` AS `doctorname`,`dr`.`providerid` AS `providerid`,`dr`.`speciality` AS `specialityid`,`sp`.`speciality` AS `speciality`,`dr`.`role` AS `roleid`,`rl`.`role` AS `role`,`dr`.`practice_owner` AS `practice_owner`,`dr`.`email` AS `email`,`dr`.`cell` AS `cell`,`dr`.`registration` AS `registration`,`dr`.`color` AS `color`,`dr`.`stafftype` AS `stafftype`,`dr`.`notes` AS `notes`,`dr`.`is_active` AS `is_active` from ((`doctor` `dr` left join `speciality` `sp` on(((`dr`.`speciality` = `sp`.`id`) and (`dr`.`providerid` = `sp`.`providerid`)))) left join `role` `rl` on(((`dr`.`role` = `rl`.`id`) and (`dr`.`providerid` = `rl`.`providerid`))));

10/24/2018
============
1. XXXxUSE `prod_dup`;
XXXCREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymenttotalpaid` AS
    SELECT 
        `payment`.`treatmentplan` AS `id`,
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`treatmentplan` AS `treatmentplan`,
        `payment`.`provider` AS `provider`,
        MAX(payment.paymentdate) AS lastpaymentdate,
        SUM(`payment`.`amount`) AS `totalpaid`
    FROM
        `payment`
    GROUP BY `payment`.`treatmentplan`;

2. XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_payments` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`id` AS `treatmentid`,
        `treatment`.`startdate` AS `treatmentdate`,
        `vw_treatment_procedure_group`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`,
        `vw_memberpatientlist`.`fullname` AS `patientname`,
        SUM(`treatmentplan`.`totaltreatmentcost`) AS `totaltreatmentcost`,
        SUM(`treatmentplan`.`totalcopay`) AS `totalcopay`,
        SUM(`treatmentplan`.`totalinspays`) AS `totalinspays`,
        `vw_paymenttotalpaid`.`totalpaid` AS `totalpaid`,
        MAX(vw_paymenttotalpaid.lastpaymentdate) as lastpaymentdate,
        ((SUM(`treatmentplan`.`totalcopay`) - SUM(`treatmentplan`.`totalinspays`)) - `vw_paymenttotalpaid`.`totalpaid`) AS `totaldue`,
        SUM(`treatmentplan`.`totalcopaypaid`) AS `totalcopaypaid`,
        SUM(`treatmentplan`.`totalinspaid`) AS `totalinspaid`,
        
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        ((((`treatmentplan`
        LEFT JOIN `vw_paymenttotalpaid` ON ((`vw_paymenttotalpaid`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `vw_treatment_procedure_group` ON ((`vw_treatment_procedure_group`.`treatmentid` = `treatment`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`primarypatientid` = `treatmentplan`.`primarypatient`)
            AND (`vw_memberpatientlist`.`patientid` = `treatmentplan`.`patient`))))
    GROUP BY `treatment`.`id` DESC , `treatment`.`startdate` DESC;


10/30/2018
===========

1. XXXXURLPROPERTIES
ALTER TABLE `prod_dup`.`urlproperties` 
ADD COLUMN `relgrprodurl` VARCHAR(512) NULL AFTER `timeinterval`,
ADD COLUMN `relgrstgurl` VARCHAR(512) NULL AFTER `relgrprodurl`;

XXXXALTER TABLE `prod_dup`.`urlproperties` 
ADD COLUMN `religare` CHAR(1) NULL DEFAULT 'F' AFTER `relgrstgurl`;


2. XXXAdd 2 columns to imporprocedurepriceplan

3. XXXXALTER TABLE `prod_dup`.`procedurepriceplan` 
ADD COLUMN `relgrproc` CHAR(1) NULL DEFAULT 'F' AFTER `is_free`,
ADD COLUMN `relgrprocdesc` VARCHAR(512) NULL DEFAULT NULL AFTER `relgrproc`;

4. XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));

5. XXXXUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan_x999` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))
    WHERE
        (`procedurepriceplan`.`is_free` = 'T');

10/31/2018
===========

1. vw_treatmentprocedure

USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `vw_procedurepriceplan`.`relgrproc` AS `relgrproc`,
        IF((`vw_procedurepriceplan`.`relgrproc` = 'T'),
            `vw_procedurepriceplan`.`relgrprocdesc`,
            NULL) AS `relgrprocdesc`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`status` AS `status`,
        `treatment_procedure`.`authorized` AS `authorized`,
        `treatment_procedure`.`remarks` AS `remarks`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`is_active` AS `is_active`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`
    FROM
        (((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));



2. XXXALTER TABLE `prod_dup`.`treatment_procedure` 
ADD COLUMN `relgrproc` CHAR(1) NULL DEFAULT 'F' AFTER `authorized`;


11/17/2018
==========
1. XXX YYY ALTER TABLE `mydentalplan$my_dentalplan_prod`.`dentalprocedure` 
ADD COLUMN `keywords` VARCHAR(255) NULL DEFAULT NULL AFTER `description`;

2.XX#YYYY USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        CONCAT(dentalprocedure.keywords,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`shortdescription`,
                                CONCAT(':',
                                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                                CONCAT(':',
                                                        CONCAT(CONCAT('UCR(',
                                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`;


3. XXXX YYYY UPDATE dentalprocedure
INNER JOIN importprocedures
    ON importprocedures.code = dentalprocedure.dentalprocedure
SET dentalprocedure.keywords = importprocedures.keys

4. XXXX#YYYY vw_procedurepriceplan
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
		CONCAT(dentalprocedure.keywords,
        CONCAT(':',
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));

5. XXX#YYYY vw_procedurepriceplan_x999
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan_x999` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
		CONCAT(dentalprocedure.keywords,
        CONCAT(':',
        CONCAT(`dentalprocedure`.`shortdescription`,
                ' : ',
                `procedurepriceplan`.`procedurecode`))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))
    WHERE
        (`procedurepriceplan`.`is_free` = 'T');

6. XXXX#YYY vw_dentalprocedure_x999
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_dentalprocedure_x999` AS
    SELECT 
        `dentalprocedure`.`id` AS `id`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`dentalprocedure` AS `proccode`,
        CONCAT(`dentalprocedure`.`keywords`,
                CONCAT(':',
        CONCAT(`dentalprocedure`.`shortdescription`,
                CONCAT(':',
                        CONCAT(`dentalprocedure`.`dentalprocedure`,
                                CONCAT(':',
                                        CONCAT(CONCAT('UCR(',
                                                        CONCAT(`dentalprocedure`.`procedurefee`,
                                                                CONCAT('):', CONCAT(`dentalprocedure`.`id`))))))))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`procedurefee` AS `procedurefee`,
        `dentalprocedure`.`is_active` AS `is_active`
    FROM
        `dentalprocedure`
    WHERE
        (`dentalprocedure`.`dentalprocedure` = 'G0100A');


7. XXX#YYY vw_appointment_monthly, weekly, today
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        doctor.cell as doccell,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE()));

8. XXXX YYY ALTER TABLE `prod_dup`.`medicaltest` 
ADD COLUMN `testdate` DATETIME NULL DEFAULT NULL AFTER `testname`;


9. XXXX#YYYvw_procedurepriceplan 
- Concat '[]'

10. XX#YYYYvw_procedurepriceplan_x999
- Concat '[]'


11. t_appointment index
ALTER TABLE `prod_dup`.`t_appointment` 
ADD INDEX `f_start_time__idx` (`f_start_time` ASC);
ALTER TABLE `prod_dup`.`t_appointment` 
DROP INDEX `f_start_time__idx` ,
ADD INDEX `f_start_time__idx` (`f_start_time` ASC, `provider` ASC);

12. XXXX#YYY vw_appointment_monthly
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_monthly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `doctor`.`cell` AS `doccell`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
		((YEAR(`t_appointment`.`f_start_time`) = YEAR(CURDATE())) AND
        (MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE())));

13. XXXX#YYYY vw_appointment_weekly
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointment_weekly` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `providerid`,
        `doctor`.`name` AS `doctorname`,
        `doctor`.`id` AS `doctorid`,
        `vw_treatmentlist`.`id` AS `treatmentid`,
        `vw_treatmentlist`.`treatment` AS `treatment`,
        `vw_treatmentlist`.`patientid` AS `patientid`,
        `vw_treatmentlist`.`memberid` AS `memberid`,
        `t_appointment`.`cell` AS `patientcell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        (CASE `t_appointment`.`newpatient`
            WHEN 'T' THEN 'New Patient'
            WHEN 'F' THEN 'Current Patient'
            ELSE 'Unknown'
        END) AS `patienttype`,
        (CASE `t_appointment`.`blockappt`
            WHEN 'T' THEN 'Appointment is blocked'
            ELSE 'T'
        END) AS `appointmentblock`,
        `doctor`.`color` AS `doccolor`,
        `t_appointment`.`color` AS `apptcolor`,
        `t_appointment`.`is_active` AS `is_active`
    FROM
        ((`t_appointment`
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)))
        LEFT JOIN `vw_treatmentlist` ON ((`vw_treatmentlist`.`id` = `t_appointment`.`f_treatmentid`)))
    WHERE
       (((YEAR(`t_appointment`.`f_start_time`) = YEAR(CURDATE())))  AND
        ((MONTH(`t_appointment`.`f_start_time`) = MONTH(CURDATE())))  AND
        ((WEEK(`t_appointment`.`f_start_time`, 0) = WEEK(CURDATE(), 0))));

14. XXXYYYYCreate a WALKIN company for WALK in patient
    company = WALKIN, is_active = False
    XXXX YYYYINSERT INTO `company` (`company`, `name`, `minsubscribers`, `is_active`, `maxsubscribers`, `dependantmode`, `authorizationrequired`) VALUES ('WALKIN', 'WALKIN', '1', 'F', '00000000004', '0', 'F');
    XXXX YYYYINSERT INTO `company` (`company`, `name`, `contact`, `address1`, `address2`, `address3`, `city`, `st`, `pin`, `telephone`, `cell`, `fax`, `email`, `enrolleddate`, `terminationdate`, `renewaldate`, `capcycle`, `premcycle`, `adminfee`, `minsubscribers`, `minsubsage`, `maxsubsage`, `mindependantage`, `maxdependantage`, `notes`, `commission`, `hmoplan`, `agent`, `groupkey`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `maxsubscribers`, `dependantmode`, `authorizationrequired`) VALUES ('RELGR', 'Religare Insurance', 'Manjunathan S', '#324 7th Cross Road', 'Defence Layout', 'Sahkar Nagar', 'Bengaluru', 'Karnataka (KA)', '560092', '1234567890', 'T', 'T', 'T', '2018-10-31', '2018-10-31', '2018-10-31', 'Annual', 'Annual', '0', '1', '1', '99', '1', '99', 'T', '0', '1', '4', 'jS1wO0', 'T', '2018-10-31 01:27:04', '1', '2018-10-31 02:58:17', '1', '00000000020', 'F', 'F');


15. Doctor
XXX YYYYALTER TABLE `prod_dup`.`doctor` 
ADD COLUMN `docsms` CHAR(1) NULL DEFAULT 'T' AFTER `notes`,
ADD COLUMN `docemail` CHAR(1) NULL DEFAULT 'T' AFTER `docsms`,
ADD COLUMN `groupsms` CHAR(1) NULL DEFAULT 'F' AFTER `docemail`,
ADD COLUMN `groupemail` CHAR(1) NULL DEFAULT 'F' AFTER `groupsms`;

16. XXX#YYYYvw_appointments (docsms,docemail,groupsms,groupemail,provtel)
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointments` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_uniqueid` AS `f_uniqueid`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`ptitle` AS `ptitle`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_end_time` AS `f_end_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_location` AS `f_location`,
        `t_appointment`.`f_treatmentid` AS `f_treatmentid`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `provider`,
        `t_appointment`.`doctor` AS `doctor`,
        `t_appointment`.`patientmember` AS `patientmember`,
        `t_appointment`.`patient` AS `patient`,
        `t_appointment`.`cell` AS `cell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        `t_appointment`.`blockappt` AS `blockappt`,
        `t_appointment`.`sendsms` AS `sendsms`,
        `t_appointment`.`is_active` AS `is_active`,
        `t_appointment`.`created_on` AS `created_on`,
        `t_appointment`.`created_by` AS `created_by`,
        `t_appointment`.`modified_on` AS `modified_on`,
        `t_appointment`.`modified_by` AS `modified_by`,
        `doctor`.`name` AS `docname`,
        `doctor`.`cell` AS `doccell`,
        `doctor`.`email` AS `docemail`,
        `doctor`.`color` AS `color`,
        `doctor`.`docsms` AS `docsms`,
        `doctor`.`docemail` AS `docemailflag`,
        `doctor`.`groupsms` AS `groupsms`,
        `doctor`.`groupemail` AS `groupemail`,
        `provider`.`cell` AS `provcell`,
        `provider`.`providername` AS `provname`,
        `provider`.`email` AS `provemail`,
        `provider`.`practicename` AS `clinic`,
        provider.telephone as provtel
    FROM
        ((`t_appointment`
        LEFT JOIN `provider` ON ((`provider`.`id` = `t_appointment`.`provider`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)));

17. XX#YYYYvw_payments
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_payments` AS
    SELECT 
        `treatmentplan`.`id` AS `id`,
        `treatment`.`treatment` AS `treatment`,
        `treatment`.`id` AS `treatmentid`,
        `treatment`.`startdate` AS `treatmentdate`,
        `vw_treatment_procedure_group`.`shortdescription` AS `shortdescription`,
        `treatmentplan`.`primarypatient` AS `memberid`,
        `treatmentplan`.`patient` AS `patientid`,
        `treatmentplan`.`provider` AS `providerid`,
        `vw_memberpatientlist`.`fullname` AS `patientname`,
        SUM(`treatmentplan`.`totaltreatmentcost`) AS `totaltreatmentcost`,
        SUM(`treatmentplan`.`totalcopay`) AS `totalcopay`,
        SUM(`treatmentplan`.`totalinspays`) AS `totalinspays`,
        IFNULL(`vw_paymenttotalpaid`.`totalpaid`,0) AS `totalpaid`,
        MAX(`vw_paymenttotalpaid`.`lastpaymentdate`) AS `lastpaymentdate`,
        ((SUM(`treatmentplan`.`totaltreatmentcost`) -  - SUM(`treatmentplan`.`totalinspays`)) - `vw_paymenttotalpaid`.`totalpaid`) AS `totaldue`,
        SUM(`treatmentplan`.`totalcopaypaid`) AS `totalcopaypaid`,
        SUM(`treatmentplan`.`totalinspaid`) AS `totalinspaid`,
        `treatmentplan`.`is_active` AS `is_active`
    FROM
        ((((`treatmentplan`
        LEFT JOIN `vw_paymenttotalpaid` ON ((`vw_paymenttotalpaid`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `treatment` ON ((`treatment`.`treatmentplan` = `treatmentplan`.`id`)))
        LEFT JOIN `vw_treatment_procedure_group` ON ((`vw_treatment_procedure_group`.`treatmentid` = `treatment`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`primarypatientid` = `treatmentplan`.`primarypatient`)
            AND (`vw_memberpatientlist`.`patientid` = `treatmentplan`.`patient`))))
    GROUP BY `treatment`.`id` DESC , `treatment`.`startdate` DESC;

18 X#YYYYvw_totalpair
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymenttotalpaid` AS
    SELECT 
        `payment`.`treatmentplan` AS `id`,
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`treatmentplan` AS `treatmentplan`,
        `payment`.`provider` AS `provider`,
        MAX(`payment`.`paymentdate`) AS `lastpaymentdate`,
        SUM(IFNULL(`payment`.`amount`,0)) AS `totalpaid`
    FROM
        `payment`
    GROUP BY `payment`.`treatmentplan`;

08/01/2019
===========

1. XXXYYYt_appointment : add sendreminder flag
ALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `sendrem` CHAR(1) NULL DEFAULT 'F' AFTER `sendsms`;
ALTER TABLE `prod_dup`.`t_appointment` 
ADD COLUMN `smsaction` VARCHAR(45) NULL DEFAULT NULL AFTER `sendrem`;

2. XXXYYYUSE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_appointments` AS
    SELECT 
        `t_appointment`.`id` AS `id`,
        `t_appointment`.`f_uniqueid` AS `f_uniqueid`,
        `t_appointment`.`f_title` AS `f_title`,
        `t_appointment`.`ptitle` AS `ptitle`,
        `t_appointment`.`f_patientname` AS `f_patientname`,
        `t_appointment`.`f_start_time` AS `f_start_time`,
        `t_appointment`.`f_end_time` AS `f_end_time`,
        `t_appointment`.`f_duration` AS `f_duration`,
        `t_appointment`.`f_location` AS `f_location`,
        `t_appointment`.`f_treatmentid` AS `f_treatmentid`,
        `t_appointment`.`f_status` AS `f_status`,
        `t_appointment`.`description` AS `description`,
        `t_appointment`.`provider` AS `provider`,
        `t_appointment`.`doctor` AS `doctor`,
        `t_appointment`.`patientmember` AS `patientmember`,
        `t_appointment`.`patient` AS `patient`,
        `t_appointment`.`cell` AS `cell`,
        `t_appointment`.`newpatient` AS `newpatient`,
        `t_appointment`.`blockappt` AS `blockappt`,
        `t_appointment`.`sendsms` AS `sendsms`,
        `t_appointment`.`sendrem` AS `sendrem`,
	`t_appointment`.`smsaction` AS `smsaction`,
        `t_appointment`.`is_active` AS `is_active`,
        `t_appointment`.`created_on` AS `created_on`,
        `t_appointment`.`created_by` AS `created_by`,
        `t_appointment`.`modified_on` AS `modified_on`,
        `t_appointment`.`modified_by` AS `modified_by`,
        `doctor`.`name` AS `docname`,
        `doctor`.`cell` AS `doccell`,
        `doctor`.`email` AS `docemail`,
        `doctor`.`color` AS `color`,
        `doctor`.`docsms` AS `docsms`,
        `doctor`.`docemail` AS `docemailflag`,
        `doctor`.`groupsms` AS `groupsms`,
        `doctor`.`groupemail` AS `groupemail`,
        `provider`.`cell` AS `provcell`,
        `provider`.`providername` AS `provname`,
        `provider`.`email` AS `provemail`,
        `provider`.`practicename` AS `clinic`,
        `provider`.`telephone` AS `provtel`
    FROM
        ((`t_appointment`
        LEFT JOIN `provider` ON ((`provider`.`id` = `t_appointment`.`provider`)))
        LEFT JOIN `doctor` ON ((`doctor`.`id` = `t_appointment`.`doctor`)));

3. XXXXYYYProvider
ALTER TABLE `provider` 
ADD COLUMN `groupsms` CHAR(1) NULL DEFAULT 'T' AFTER `is_active`,
ADD COLUMN `groupemail` CHAR(1) NULL DEFAULT 'T' AFTER `groupsms`;

  
4. XXXYYYY otplog 
CREATE TABLE `otplog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `memberid` int(11) DEFAULT NULL,
  `patientid` int(11) DEFAULT NULL,
  `otp` varchar(45) DEFAULT NULL,
  `cell` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `otpdatetime` varchar(45) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;


5. XXXXYYYLogHistory
CREATE TABLE `loghistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) DEFAULT NULL,
  `logstatus` char(1) DEFAULT 'T',
  `logerror` varchar(45) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `created_by` varchar(45) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


01/22/2019
==========
1. XXXXYYYYvw_paymentlist  - added payment.fp_invoice

2. XXXXXYYYYmodified activity_tracker table : added paymentinvoice
ALTER TABLE `prod_dup`.`activitytracker` 
ADD COLUMN `paymentinvoice` VARCHAR(45) NULL DEFAULT NULL AFTER `paymentmode`;

02/05/2019
==========
3. XXXXYYYY USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymenttotalpaid` AS
    SELECT 
        `payment`.`treatmentplan` AS `id`,
        `payment`.`patientmember` AS `patientmember`,
        `payment`.`treatmentplan` AS `treatmentplan`,
        `payment`.`provider` AS `provider`,
        MAX(`payment`.`paymentdate`) AS `lastpaymentdate`,
        SUM(IFNULL(`payment`.`amount`, 0)) AS `totalpaid`
    FROM
        `payment`
	where payment.paymentcommit = 'T' and payment.is_active = 'T'
    GROUP BY `payment`.`treatmentplan`;
    
4. XXXXYYYY vw_memberpatientlist - check for patientmember dob for age calculation

5. XXXXYYY update patientmember set city = '--Select City--' where city = 'T' or city = 'None' or city is NULL

6. XXXXYYYYRemove otphistory from all db.  otphistory is replaced with otplog

02/15/2019
===========

XXXXupdate payment set paymentcommit = 'T' and fp_status = 'S' where paymentmode = 'Cash' or paymentmode = 'Cheque' or paymentmode = 'Cashless'
XXXXupdate payment set paymentcommit = 'T' where paymentmode = 'Credit' and paymentcommit ='F'  and (fp_status = 'S' or fp_status = 'X')
clean payment data
clean provider data
clean member data


1.XXXXZZZZvw_paymenttxlog
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_paymenttxlog` AS
    SELECT 
        `paymenttxlog`.`txno` AS `txno`,
        `paymenttxlog`.`txdatetime` AS `txdatetime`,
        `paymenttxlog`.`txamount` AS `txamount`,
        `paymenttxlog`.`responsecode` AS `responsecode`,
        `paymenttxlog`.`responsemssg` AS `responsemssg`,
        `paymenttxlog`.`paymentid` AS `paymentid`,
        `paymenttxlog`.`paymentamount` AS `paymentamount`,
        `paymenttxlog`.`paymentdate` AS `paymentdate`,
        `paymenttxlog`.`paymenttxid` AS `paymenttxid`,
        `paymenttxlog`.`servicetax` AS `servicetax`,
        `paymenttxlog`.`swipecharge` AS `swipecharge`,
        `paymenttxlog`.`total` AS `total`,
        `paymenttxlog`.`webmember` AS `webmemberid`,
		`paymenttxlog`.`patientmember` AS `memberid`,
        `webmember`.`fname` AS `FirstName`,
        `webmember`.`lname` AS `LastName`,
        `webmember`.`webmember` AS `webmember`,
        `paymenttxlog`.`is_active` AS `is_active`,
        `company`.`name` AS `companyname`,
        `company`.`company` AS `companycode`
    FROM
        ((`paymenttxlog`
        LEFT JOIN `webmember` ON ((`webmember`.`id` = `paymenttxlog`.`webmember`)))
        LEFT JOIN `company` ON ((`company`.`id` = `webmember`.`company`)))
    ORDER BY `company`.`name`;


2. XXXXZZZZvw_memberpaymentx
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpaymentx` AS
    SELECT 
        `vw_paymenttxlog`.`memberid` AS `memberid`,
        MAX(`vw_paymenttxlog`.`txdatetime`) AS `paymentdate`,
        SUM(`vw_paymenttxlog`.`total`) AS `amount`
    FROM
        `vw_paymenttxlog`
    WHERE
        ((`vw_paymenttxlog`.`responsecode` <> '999')
            AND (`vw_paymenttxlog`.`is_active` = 'T'))
    GROUP BY `vw_paymenttxlog`.`memberid`
    ORDER BY `vw_paymenttxlog`.`memberid`
    
3. XXXZZZZnew view - vw_providerrevenueYTD
USE `prod_dup`;
CREATE  OR REPLACE VIEW `vw_providerreveniewYTD` AS
select vw_paymentlist.providerid, YEAR(vw_paymentlist.paymentdate) as paymentyear, SUM(vw_paymentlist.amount) as earnedrevenue 
from vw_paymentlist
left join patientmember on (patientmember.id = vw_paymentlist.memberid)
left join provider on (provider.id = vw_paymentlist.providerid)
where 
patientmember.is_active = 'T' and patientmember.hmopatientmember = 'T' and
vw_paymentlist.is_active = 'T' and vw_paymentlist.paymentcommit = 'T' and
vw_paymentlist.fppaymentstatus = 'S' and  provider.is_active = 'T'
group by paymentyear, vw_paymentlist.providerid;
USE `prod_dup`;
CREATE  OR REPLACE VIEW `vw_providerreveniewYTD` AS
select vw_paymentlist.providerid, YEAR(vw_paymentlist.paymentdate) as paymentyear, SUM(vw_paymentlist.amount) as earnedrevenue 
from vw_paymentlist
left join patientmember on (patientmember.id = vw_paymentlist.memberid)
left join provider on (provider.id = vw_paymentlist.providerid)
where 
patientmember.is_active = 'T' and patientmember.hmopatientmember = 'T' and
vw_paymentlist.is_active = 'T' and vw_paymentlist.paymentcommit = 'T' and
vw_paymentlist.fppaymentstatus = 'S' and  provider.is_active = 'T'
group by paymentyear, vw_paymentlist.providerid;


4. XXXxZZZZvw_providertotalrevenue

5. vw_treatmentprocedure
LEFT join function has to be changed

6 XXXXZZZvw_memberdata
USE `prod_dup`;
CREATE  OR REPLACE VIEW `vw_memberdata` AS
SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'P' AS `patienttype`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`mname` AS `mname`,
        `patientmember`.`lname` AS `lname`,
        patientmember.address1 as address1,
        patientmember.address2 as address2,
        patientmember.address3 as address3,
        patientmember.city as city,
        patientmember.st as st,
        patientmember.pin as pin,
	    `patientmember`.`cell` AS `cell`,
	    `patientmember`.`email` AS `email`,
	    `patientmember`.`dob` AS `dob`,
	    `patientmember`.`gender` AS `gender`,
	'Self' AS `relation`,
	`patientmember`.`status` AS `status`,
        patientmember.premium as premium,
		patientmember.renewed as renewed,
        patientmember.upgraded as upgraded,
        `patientmember`.`is_active` AS `is_active`,
		CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        company.company as companycode,
        provider.provider as provider,
        provider.address1 as provaddress1,
        provider.address2 as provaddress2,
        provider.address3 as provaddress3,
        provider.city as provcity,
        provider.st as provst,
        provider.pin as provpin,
        provider.cell as provcell,
        provider.email as provemail,
        provider.is_active as provactive,
        company.is_active as compactive,
        hmoplan.is_active as hmoactive
      
    FROM
        `patientmember`
        LEFT JOIN `hmoplan` ON (`patientmember`.`hmoplan` = `hmoplan`.`id`)
        LEFT JOIN company ON (patientmember.company = company.id)
		LEFT JOIN provider on (patientmember.provider = provider.id)
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`mname` AS `mname`,
        `patientmemberdependants`.`lname` AS `lname`,
        patientmember.address1 as address1,
        patientmember.address2 as address2,
        patientmember.address3 as address3,
        patientmember.city as city,
        patientmember.st as st,
        patientmember.pin as pin,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmemberdependants`.`relation` AS `relation`,
        
	   `patientmember`.`status` AS `status`,
		 0 as premium,
		patientmember.renewed as renewed,
        patientmember.upgraded as upgraded,
        `patientmemberdependants`.`is_active` AS `is_active`,
		CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        company.company as companycode,
        provider.provider as provider,
        provider.address1 as provaddress1,
        provider.address2 as provaddress2,
        provider.address3 as provaddress3,
        provider.city as provcity,
        provider.st as provst,
        provider.pin as provpin,
        provider.cell as provcell,
        provider.email as provemail,
        provider.is_active as provactive,
        company.is_active as compactive,
        hmoplan.is_active as hmoactive
      
    FROM

        `patientmemberdependants`
        LEFT JOIN `patientmember` ON (`patientmember`.`id` = `patientmemberdependants`.`patientmember`)
        LEFT JOIN `hmoplan` ON (`patientmember`.`hmoplan` = `hmoplan`.`id`)
        LEFT JOIN company ON (patientmember.company = company.id)
		LEFT JOIN provider on (patientmember.provider = provider.id)
        
    where (patientmember.hmopatientmember = 'T')
    ORDER BY patientmember,patienttype desc;


02/26/2019
==========
1. XXXXZZZZvw_memberpaymentreport
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_memberpaymentreport` AS select `payment`.`id` AS `id`,`payment`.`fp_paymentref` AS `fppaymentref`,`payment`.`fp_paymenttype` AS `fppaymenttype`,`payment`.`fp_invoice` AS `fpinvoice`,`payment`.`fp_paymentdate` AS `paymentdate`,`payment`.`fp_invoiceamt` AS `invoiceamount`,`payment`.`fp_amount` AS `paymentamount`,'P' AS `patienttype`,`patientmember`.`patientmember` AS `patientmember`,`patientmember`.`fname` AS `fname`,`patientmember`.`mname` AS `mname`,`patientmember`.`lname` AS `lname`,`patientmember`.`city` AS `city`,`patientmember`.`st` AS `st`,`patientmember`.`pin` AS `pin`,`patientmember`.`cell` AS `cell`,`patientmember`.`email` AS `email`,`provider`.`provider` AS `provider`,`provider`.`practicename` AS `practicename`,`provider`.`city` AS `provcity`,`provider`.`st` AS `provst`,`provider`.`pin` AS `provpin`,`provider`.`cell` AS `provcell`,`provider`.`email` AS `provemail`,`treatment`.`id` AS `treatmentid`,`treatment`.`treatment` AS `treatment`,`vw_treatment_procedure_group`.`shortdescription` AS `shortdescription`,`treatmentplan`.`totaltreatmentcost` AS `totaltreatmentcost`,`treatmentplan`.`totalcopay` AS `totalcopay`,`treatmentplan`.`totalinspays` AS `totalinspays`,`treatmentplan`.`totalpaid` AS `totalpaid`,`treatmentplan`.`totalcopaypaid` AS `totalcopaypaid`,`treatmentplan`.`totalinspaid` AS `totalinspaid`,`treatmentplan`.`totaldue` AS `totaldue` from (((((`payment` left join `patientmember` on((`patientmember`.`id` = `payment`.`patientmember`))) left join `provider` on((`provider`.`id` = `payment`.`provider`))) left join `treatmentplan` on((`treatmentplan`.`id` = `payment`.`treatmentplan`))) left join `treatment` on((`treatment`.`treatmentplan` = `treatmentplan`.`id`))) left join `vw_treatment_procedure_group` on((`vw_treatment_procedure_group`.`treatmentid` = `treatment`.`id`))) where ((`payment`.`paymentcommit` = 'T') and (`payment`.`is_active` = 'T') and (`payment`.`fp_status` = 'S') and (`payment`.`is_active` = 'T') and (`patientmember`.`hmopatientmember` = 'T') and (`provider`.`is_active` = 'T') and (`treatment`.`is_active` = 'T') and (`treatmentplan`.`is_active` = 'T')) order by `patientmember`.`patientmember`,`treatment`.`treatment`;

02/27/2019
==========
1. XXXXZZZZvw_memberdata
2. XXXXZZZZvw_memberpatientlist

03/22/2019
==========
0. XXXZZZZYYYadd religare regions in groupregion table  - DELS, MUMS

INSERT INTO `groupregion` (`groupregion`, `region`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`) 
VALUES ('DELS', 'Delhi South', 'T', '2019-04-12 22:56:07', '1', '2019-04-12 22:56:07', '1');
INSERT INTO `groupregion` (`groupregion`, `region`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`) 
VALUES ('MUMS', 'Mumbai South', 'T', '2019-04-12 22:56:40', '1', '2019-04-12 22:56:40', '1');


0. XXXXZZZYYYYadd RLG company in company table 
UPDATE `prod_dup`.`company` SET `company`='RLG' WHERE `id`='103';

INSERT INTO `company` ( `company`, `name`, `contact`, `address1`, `address2`, `address3`, `city`, `st`, `pin`, `telephone`, `cell`, `fax`, 
`email`, `enrolleddate`, `terminationdate`, `renewaldate`, `capcycle`, `premcycle`, `adminfee`, `minsubscribers`, `minsubsage`, `maxsubsage`, 
`mindependantage`, `maxdependantage`, `notes`, `commission`, `hmoplan`, `agent`, `groupkey`, `is_active`, `created_on`, `created_by`, 
`modified_on`, `modified_by`, `maxsubscribers`, `dependantmode`, `authorizationrequired`) 
VALUES ( 'RLG', 'Religare Health Insurance Co. Ltd.,', 'MDP', '123', '456', '789', 'Bengaluru', 'Karnataka (KA)', '560092', '18001027526', 
'T', 'T', 'T', '2019-04-12', '2019-04-12', '2019-04-12', 'Annual', 'Annual', '0', '1', '1', '99', '1', '99', 'T', '0', '1', '3', 
'fP8dW8', 'T', '2019-04-12 22:02:45', '1', '2019-04-12 22:03:17', '1', '00000000020', 'F', 'F');

0. XXXZZZYYYYadd religare  plans in hmoplan table
RLGDELS101, RGLMUMS101, RLGGUR101,RLGDEL102,RLGMUM102,RLGNOI102,RLGGHZ102, RLGTNA102
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGDELS101', 'RLG PREMIUM DENTAL PLAN (RLG 101)', 'RLG101', 'T', '2019-03-28 13:15:59', '1', '2019-03-28 13:17:38', '1', 'RLG PREMIUM DENTAL PLAN (RLG 101).pdf', '96', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGMUMS101', 'RLG PREMIUM DENTAL PLAN (RLG 101)', 'RLG101', 'T', '2019-03-28 13:18:11', '1', '2019-03-28 13:18:34', '1', 'RLG PREMIUM DENTAL PLAN (RLG 101).pdf', '97', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGGUR101', 'RLG PREMIUM DENTAL PLAN (RLG 101)', 'RLG101', 'T', '2019-03-28 13:19:04', '1', '2019-03-28 13:22:28', '1', 'RLG PREMIUM DENTAL PLAN (RLG 101).pdf', '8', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGDEL102', 'RLG PREMIUM DENTAL PLAN (RLG 102)', 'RLG102', 'T', '2019-03-28 13:22:58', '1', '2019-03-28 13:23:24', '1', 'RLG PREMIUM DENTAL PLAN (RLG 102).pdf', '4', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGMUM102', 'RLG PREMIUM DENTAL PLAN (RLG 102)', 'RLG102', 'T', '2019-03-28 13:24:11', '1', '2019-03-28 13:26:31', '1', 'RLG PREMIUM DENTAL PLAN (RLG 102).pdf', '6', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGNOI102', 'RLG PREMIUM DENTAL PLAN (RLG 102)', 'RLG102', 'T', '2019-03-28 13:26:59', '1', '2019-03-28 13:27:52', '1', 'RLG PREMIUM DENTAL PLAN (RLG 102).pdf', '9', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGGHZ102', 'RLG PREMIUM DENTAL PLAN (RLG 102)', 'RLG102', 'T', '2019-03-28 13:28:20', '1', '2019-03-28 13:29:17', '1', 'RLG PREMIUM DENTAL PLAN (RLG 102).pdf', '12', 'MyDentalPlanMemberWelcomeLetter.html');
INSERT INTO `hmoplan` ( `hmoplancode`, `name`, `procedurepriceplancode`, `is_active`, `created_on`, `created_by`, `modified_on`, `modified_by`, `planfile`, `groupregion`, `welcomeletter`) VALUES ( 'RLGTNA102', 'RLG PREMIUM DENTAL PLAN (RLG 102)', 'RLG102', 'T', '2019-03-28 13:29:36', '1', '2019-03-28 13:30:45', '1', 'RLG PREMIUM DENTAL PLAN (RLG 102).pdf', '23', 'MyDentalPlanMemberWelcomeLetter.html');


0. XXXXZZZZYYYYadd RLG default member count row in membercount table for RLGR company


0. XXXXZZZYYYYCreate importrlgprovider
CREATE TABLE `importrlgprovider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providercode` varchar(45) DEFAULT NULL,
  `region` varchar(45) DEFAULT NULL,
  `plan` varchar(45) DEFAULT NULL,
  `providerid` int(11) DEFAULT '0',
  `regionid` int(11) DEFAULT '0',
  `planid` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8;


1. XXXZZZZYYYYcreate rlgrprovider table
CREATE TABLE `rlgprovider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providerid` int(11) DEFAULT NULL,
  `providercode` varchar(45) DEFAULT NULL,
  `regionid` int(11) DEFAULT NULL,
  `planid` int(11) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=114 DEFAULT CHARSET=utf8;


2. XXXXZZZZYYYYmodify importprocedurepriceplan

ALTER TABLE `importprocedurepriceplan` 
ADD COLUMN `service_id` VARCHAR(45) NULL DEFAULT NULL AFTER `Remarks`,
ADD COLUMN `service_name` VARCHAR(128) NULL DEFAULT NULL AFTER `service_id`,
ADD COLUMN `service_category` VARCHAR(128) NULL DEFAULT NULL AFTER `service_name`;

3. XXXXZZZZZYYYmodify procedurepriceplan
ALTER TABLE procedurepriceplan` 
ADD COLUMN `service_id` VARCHAR(45) NULL DEFAULT NULL AFTER `modified_on`,
ADD COLUMN `service_name` VARCHAR(128) NULL DEFAULT NULL AFTER `service_id`,
ADD COLUMN `service_category` VARCHAR(128) NULL DEFAULT NULL AFTER `service_name`;

4. XXXZZZZYYYmodify vw_procedurepriceplan
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT('[',
                CONCAT(`dentalprocedure`.`keywords`,
                        CONCAT(']',
                                CONCAT(':',
                                        CONCAT(`dentalprocedure`.`shortdescription`,
                                                ' : ',
                                                `procedurepriceplan`.`procedurecode`))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`service_id` AS `service_id`,
        `procedurepriceplan`.`service_name` AS `service_name`,
        `procedurepriceplan`.`service_category` AS `service_category`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));

5.XXXZZZZYYYYmodify vw_procedurepriceplan_x999
USE `prod_dup`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_procedurepriceplan_x999` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT('[',
                CONCAT(`dentalprocedure`.`keywords`,
                        CONCAT(']',
                                CONCAT(':',
                                        CONCAT(`dentalprocedure`.`shortdescription`,
                                                ' : ',
                                                `procedurepriceplan`.`procedurecode`))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`service_id` AS `service_id`,
        `procedurepriceplan`.`service_name` AS `service_name`,
        `procedurepriceplan`.`service_category` AS `service_category`,
        
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)))
    WHERE
        (`procedurepriceplan`.`is_free` = 'T');

6. XXXZZZYYYimport religare providers

7. XXXZZZZYYYYimport procedure price plan with service_id ....

8. XXXXZZZYYYYURLPropertis - RLGR URL, API Keyy
ALTER TABLE `prod_dup`.`urlproperties` 
ADD COLUMN `relgrapikey` VARCHAR(45) NULL AFTER `religare`;

9. XXXXZZZZZYYYYCreate rlgservices
CREATE TABLE `rlgservices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ackid` varchar(45) DEFAULT NULL,
  `service_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=164 DEFAULT CHARSET=utf8;


10. XXXXZZZZYYYYAlter Treatment_procedure = add col relgrtransactionid  & relgrtransactionamt


 
ALTER TABLE `mydp_stg`.`treatment_procedure` 
ADD COLUMN `relgrtransactionid` VARCHAR(45) NULL DEFAULT NULL AFTER `relgrproc`,
ADD COLUMN `relgrtransactionamt` DOUBLE NULL DEFAULT 0 AFTER `relgrtransactionid`,
ADD COLUMN `service_id` VARCHAR(45) NULL DEFAULT NULL AFTER `relgrtransactionamt`;


11. XXXXZZZZYYYvw_treatmentprocedure - added relgrtransactionid
USE `mydp_stg`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_treatmentprocedure` AS
    SELECT 
        `treatment_procedure`.`id` AS `id`,
        `treatment_procedure`.`treatmentid` AS `treatmentid`,
        `vw_procedurepriceplan`.`procedurecode` AS `procedurecode`,
        `vw_procedurepriceplan`.`altshortdescription` AS `altshortdescription`,
        `vw_procedurepriceplan`.`relgrproc` AS `relgrproc`,
        IF((`vw_procedurepriceplan`.`relgrproc` = 'T'),
            `vw_procedurepriceplan`.`relgrprocdesc`,
            NULL) AS `relgrprocdesc`,
        `treatment_procedure`.`ucr` AS `ucrfee`,
        `treatment_procedure`.`procedurefee` AS `procedurefee`,
        `treatment_procedure`.`copay` AS `copay`,
        `treatment_procedure`.`inspays` AS `inspays`,
        `treatment_procedure`.`companypays` AS `companypays`,
        `treatment_procedure`.`quadrant` AS `quadrant`,
        `treatment_procedure`.`tooth` AS `tooth`,
        `treatment_procedure`.`status` AS `status`,
        `treatment_procedure`.`authorized` AS `authorized`,
        `treatment_procedure`.`remarks` AS `remarks`,
        `treatment_procedure`.`treatmentdate` AS `treatmentdate`,
        `treatment_procedure`.`relgrtransactionid` AS `relgrtransactionid`,
        `treatment_procedure`.`relgrtransactionamt` AS `relgrtransactionamt`,
        `treatment_procedure`.`service_id` AS `service_id`,
        `treatment_procedure`.`is_active` AS `is_active`,
        `treatmentplan`.`primarypatient` AS `primarypatient`,
        `treatmentplan`.`patient` AS `patient`,
        `treatmentplan`.`treatmentplan` AS `treatmentplan`,
        `treatmentplan`.`provider` AS `providerid`,
        `treatment`.`treatment` AS `treatment`
    FROM
        (((`treatment_procedure`
        LEFT JOIN `treatment` ON ((`treatment`.`id` = `treatment_procedure`.`treatmentid`)))
        LEFT JOIN `treatmentplan` ON ((`treatmentplan`.`id` = `treatment`.`treatmentplan`)))
        LEFT JOIN `vw_procedurepriceplan` ON ((`vw_procedurepriceplan`.`id` = `treatment_procedure`.`dentalprocedure`)));

12. Modify XXXXZZZZYYYYrglprovider with is_active = Treu


15/04/2019
==========
1. Added cell in auth_user

XXXYYYZZZALTER TABLE `mydp_stg`.`auth_user` 
ADD COLUMN `cell` VARCHAR(45) NULL DEFAULT NULL AFTER `email`;

2. XXXXYYYZZZZModify auth_user
   UPDATE auth_user
INNER JOIN provider
    ON auth_user.sitekey = provider.sitekey
SET auth_user.cell = provider.cell


24/04/2019
===========
1. XXXYYYZZZZAdded relgrprocedurefee, relgrcopay, relgrinspays cols in procedurepriceplan table
ALTER TABLE `mydp_stg`.`procedurepriceplan` 
ADD COLUMN `relgrprocfee` DOUBLE NULL DEFAULT 0 AFTER `service_category`,
ADD COLUMN `relgrcopay` DOUBLE NULL DEFAULT 0 AFTER `relgrprocfee`,
ADD COLUMN `relgrinspays` DOUBLE NULL DEFAULT 0 AFTER `relgrcopay`;

2. XXXYYYZZZZSet relgrprocfee = procedurefee
update procedurepriceplan set relgrprocfee = procedurefee, copay=procedurefee, procedurefee = 0
where procedurepriceplancode = 'RLG102' and relgrproc = 'T'
update procedurepriceplan set relgrprocfee = procedurefee, copay=procedurefee, procedurefee = 0
where procedurepriceplancode = 'RLG101' and relgrproc = 'T'

3.XXXXYYYZZZZIn procedurepriceplan Update copay to base procedurefee like in SC102

4. XXXYYYZZZZvw_procedurepriceplan_relgr
USE `mydp_stg`;
CREATE 
   
 OR REPLACE VIEW `vw_procedurepriceplan_relgr` AS
    SELECT 
        `procedurepriceplan`.`id` AS `id`,
        `procedurepriceplan`.`providerid` AS `providerid`,
        `procedurepriceplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `procedurepriceplan`.`procedurecode` AS `procedurecode`,
        CONCAT(`procedurepriceplan`.`procedurecode`,
                ' : ',
                `dentalprocedure`.`shortdescription`) AS `longprocedurecode`,
        CONCAT('[',
                CONCAT(`dentalprocedure`.`keywords`,
                        CONCAT(']',
                                CONCAT(':',
                                        CONCAT(`dentalprocedure`.`shortdescription`,
                                                ' : ',
                                                `procedurepriceplan`.`procedurecode`))))) AS `shortdescription`,
        `dentalprocedure`.`shortdescription` AS `altshortdescription`,
        `dentalprocedure`.`description` AS `description`,
        `dentalprocedure`.`category` AS `category`,
        `dentalprocedure`.`id` AS `procedureid`,
        `procedurepriceplan`.`ucrfee` AS `ucrfee`,
        `procedurepriceplan`.`procedurefee` AS `procedurefee`,
        `procedurepriceplan`.`copay` AS `copay`,
        `procedurepriceplan`.`inspays` AS `inspays`,
        `procedurepriceplan`.`relgrprocfee` AS `relgrprocfee`,
        `procedurepriceplan`.`relgrcopay` AS `relgrcopay`,
        `procedurepriceplan`.`relgrinspays` AS `relgrinspays`,
        `procedurepriceplan`.`companypays` AS `companypays`,
        `procedurepriceplan`.`remarks` AS `remarks`,
        `procedurepriceplan`.`is_free` AS `is_free`,
        `procedurepriceplan`.`relgrproc` AS `relgrproc`,
        `procedurepriceplan`.`relgrprocdesc` AS `relgrprocdesc`,
        `procedurepriceplan`.`service_id` AS `service_id`,
        `procedurepriceplan`.`service_name` AS `service_name`,
        `procedurepriceplan`.`service_category` AS `service_category`,
        `procedurepriceplan`.`is_active` AS `is_active`
    FROM
        (`procedurepriceplan`
        LEFT JOIN `dentalprocedure` ON ((`dentalprocedure`.`dentalprocedure` = `procedurepriceplan`.`procedurecode`)));

4/30/2019
=========

1. XXXYYYZZZRemove order by in vw_treatmentlist

2. XXXYYYZZZ`vw_relgrtreatmentprocedure`

3. XXXYYYZZZZvw_rlgprovider

5/3/2019
=========

1. XXXYYYZZZZALTER TABLE `mydp_stg`.`urlproperties` 
ADD COLUMN `relgrpolicynumber` VARCHAR(45) NULL DEFAULT NULL AFTER `relgrapikey`;

5/7/2019
========
1. XXXXYYYYZZZCREATE TABLE `mydp_stg`.`rlgerrormessage` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(45) NULL DEFAULT NULL,
  `internalmessagemessage` VARCHAR(512) NULL DEFAULT NULL,
  `externalmessagemessage` VARCHAR(512) NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  PRIMARY KEY (`id`));
  
2. XXXXYYYYZZZZZInsert Data
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('1', 'MDP001', 'Invalid policy number and mobile number provided,', 'Invalid policy number and mobile number provided,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('2', 'MDP002', 'Please provide Customer Id OR Mobile number and Policy number,', 'Please provide Customer Id OR Mobile number and Policy number,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('3', 'MDP003', 'Acknowledgement Id can not be blank,', 'Acknowledgement Id can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('4', 'MDP004', 'OTP can not be blank,', 'OTP can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('5', 'MDP005', 'Invalid OTP,', 'Invalid OTP,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('6', 'MDP006', 'Expired OTP,', 'Expired OTP,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('7', 'MDP007', 'Transaction already completed,', 'Transaction already completed,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('8', 'MDP008', 'OPD Info does not exists,', 'OPD Info does not exists,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('9', 'MDP009', 'Error in mail sending,', 'Error in mail sending,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('10', 'MDP010', 'Acknowledgement Id DOESNT EXISTS,', 'Acknowledgement Id DOESNT EXISTS,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('11', 'MDPDB1', 'something went wrong. Please try again.,', 'something went wrong. Please try again.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('12', 'MDP011', 'Invalid Request,', 'Invalid Request,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('13', 'MDP012', 'Request already processed or time out.,', 'Request already processed or time out.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('14', 'MDP013', 'Insufficient amount error.,', 'Insufficient amount error.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('15', 'MDP014', 'Swipe Amount can not be blank or zero,', 'Swipe Amount can not be blank or zero,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('16', 'MDP015', 'Treatment Code can not be blank,', 'Treatment Code can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('17', 'MDP016', 'Treatment Name can not be blank,', 'Treatment Name can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('18', 'MDP017', 'Service Id can not be blank,', 'Service Id can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('19', 'MDP018', 'Transaction Id already completed or Invalid,', 'Transaction Id already completed or Invalid,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('20', 'MDP019', 'Transaction Id can not be blank,', 'Transaction Id can not be blank,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('21', 'MDP020', 'Transaction Id does not exist in the system,', 'Transaction Id does not exist in the system,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('22', 'MDP021', 'Transaction already settled or voided.,', 'Transaction already settled or voided.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('23', 'MDP022', 'Not able to validate customer info.,', 'Not able to validate customer info.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('24', 'MDP023', 'Document is missing. Please upload a document,', 'Document is missing. Please upload a document,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('25', 'MDP024', 'Invalid document type.,', 'Invalid document type.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('26', 'MDP025', 'Not able to upload document.,', 'Not able to upload document.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('27', 'MDP026', 'OTP can be sent.,', 'OTP can be sent.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('28', 'MDP027', 'Transaction Failed.,', 'Transaction Failed.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('29', 'MDP028', 'Settlement of Transaction Failed.,', 'Settlement of Transaction Failed.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('30', 'MDP029', 'Cannot Void non-Religare Transaction.,', 'Cannot Void non-Religare Transaction.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('31', 'MDP099', 'Error in response from the Server.,', 'Error in response from the Server.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('32', 'MDP100', 'System Exception Error.,', 'System Exception Error.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('33', 'MDP101', 'Error in creating Religare Patient.,', 'Error in creating Religare Patient.,', 'T');
INSERT INTO `mydp_stg`.`rlgerrormessage` (`id`, `code`, `internalmessage`, `externalmessage`, `is_active`) VALUES ('34', 'MDP102', 'Invalid Religare Patient.,', 'Invalid Religare Patient.,', 'T');



05/24/2019
==========

1. XXXXYYYYZZZZAdded DICOM fields in dentalimage table
ALTER TABLE `mydp_stg`.`dentalimage` 
ADD COLUMN `dicomUserUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `provider`,
ADD COLUMN `dicomAcctUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomUserUuid`,
ADD COLUMN `dicomInstUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomAcctUuid`,
ADD COLUMN `dicomPatName` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomInstUuid`,
ADD COLUMN `dicomPatUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatName`,
ADD COLUMN `dicomPatid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatUuid`,
ADD COLUMN `dicomPatOrderUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatid`,
ADD COLUMN `dicomProcDesc` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatOrderUuid`,
ADD COLUMN `dicomPerformedDate` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomProcDesc`,
ADD COLUMN `dicomURL` VARCHAR(255) NULL DEFAULT NULL AFTER `dicomPerformedDate`;


05/29/2019
==========
1. XXXYYYZZZAdd MDP103 error message
2. XXXYYYZZZZUpdate latest error messages 
06/12/2019
==========
1. Added encryption flag in urlproperties
XXXYYYZZZADD COLUMN `encryption` CHAR(1) NULL DEFAULT 'T' AFTER `relgrpolicynumber`;

06/20/2019
===========
1. XXXYYYZZZcreated new table rlgdocument
CREATE TABLE `mydp_stg`.`rlgdocument` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `docdate` DATETIME NULL,
  `rlgdocument` VARCHAR(512) NULL,
  `membername` VARCHAR(45) NULL,
  `ackid` VARCHAR(45) NULL,
  `policy_number` VARCHAR(45) NULL,
  `customer_id` VARCHAR(45) NULL,
  `mobile_number` VARCHAR(45) NULL,
  `is_active` CHAR(1) NULL,
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));
ALTER TABLE `mydp_stg`.`rlgdocument` 
ADD COLUMN `rlgdocument_filename` VARCHAR(255) NULL AFTER `rlgdocument`;

26/07/2019 
===========
1. XXXXYYYYZZZZModified dentalprocedure_chart table
Procedure code = x0080 for Root Canal

2. XXXXYYYYZZZZCreated new table Provider_bank
CREATE TABLE `providerbank` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bankname` varchar(255) DEFAULT NULL,
  `bankbranch` varchar(512) DEFAULT NULL,
  `bankaccountno` varchar(45) DEFAULT NULL,
  `bankaccounttype` varchar(45) DEFAULT NULL,
  `bankmicrno` varchar(45) DEFAULT NULL,
  `bankifsccode` varchar(45) DEFAULT NULL,
  `cancelledcheque` varchar(2048) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

INSERT INTO `providerbank` (`bankname`, `bankbranch`, `bankaccountno`, `bankaccounttype`, `bankmicrno`, `bankifsccode`, `cancelledcheque`, `is_active`, `created_by`, `created_on`, `modified_by`, `modified_on`) 
VALUES 
('NOBANK', 'NOBRANCH', 'NOACCOUNT', 'NOACCOUNTTYPE', 'NOMICRNO', 'NOIFSCCODE', 'NOCHEQUE', 'F', 1, '2019-01-01', 1, '2019-01-01');

3. XXXXYYYYZZZZModify Provider table 

ALTER TABLE `provider` 
ADD COLUMN `pa_hours` VARCHAR(512) NULL AFTER `pa_practicepin`,
ADD COLUMN `bankid` INT(11) NULL DEFAULT 1 AFTER `groupemail`;
ALTER TABLE `provider` 
ADD COLUMN `pa_longtitude` VARCHAR(128) NULL AFTER `pa_hours`,
ADD COLUMN `pa_latitude` VARCHAR(128) NULL AFTER `pa_longtitude`;
ALTER TABLE `provider` 
ADD COLUMN `pa_locationurl` VARCHAR(1024) NULL DEFAULT 'https://www.google.com/maps/dir/' AFTER `pa_latitude`;
ALTER TABLE `provider` 
ADD INDEX `provider_ibfk_bank_idx` (`bankid` ASC);
ALTER TABLE `provider` 
ADD CONSTRAINT `provider_ibfk_bank`
  FOREIGN KEY (`bankid`)
  REFERENCES `providerbank` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


4/7/2019
========
1. XXXXYYYZZZZAdded 'procdesc'

USE `mydp_stg`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_relgrtreatmentprocedure` AS
    SELECT 
        `rlgprovider`.`providerid` AS `providerid`,
        `rlgprovider`.`providercode` AS `providercode`,
        `provider`.`pa_providername` AS `providername`,
        `provider`.`pa_practicename` AS `practicename`,
        `provider`.`pa_regno` AS `regno`,
        `provider`.`pa_practiceaddress` AS `practiceaddress`,
        
        `vw_treatmentprocedure`.`treatment` AS `treatment`,
        `vw_treatmentprocedure`.`treatmentdate` AS `treatmentdate`,
        `vw_treatmentprocedure`.`service_id` AS `service_id`,
        `vw_treatmentprocedure`.`procedurecode` AS `procedurecode`,
        `vw_treatmentprocedure`.`altshortdescription` AS `procdesc`,
        `vw_treatmentprocedure`.`procedurefee` AS `procedurefee`,
        `vw_treatmentprocedure`.`copay` AS `copay`,
        `vw_treatmentprocedure`.`inspays` AS `inspays`,
        `vw_treatmentprocedure`.`tooth` AS `tooth`,
        `vw_treatmentprocedure`.`quadrant` AS `quadrant`,

        `vw_treatmentprocedure`.`relgrprocdesc` AS `relgrprocdesc`,
        `vw_treatmentprocedure`.`relgrproc` AS `relgrproc`,
        `vw_treatmentprocedure`.`status` AS `status`,
        `vw_treatmentprocedure`.`is_active` AS `is_active`,
        `vw_treatmentprocedure`.`relgrtransactionid` AS `relgrtransactionid`
    FROM
        ((`rlgprovider`
        LEFT JOIN `provider` ON ((`provider`.`id` = `rlgprovider`.`providerid`)))
        LEFT JOIN `vw_treatmentprocedure` ON (((`vw_treatmentprocedure`.`providerid` = `rlgprovider`.`providerid`)
            AND (`vw_treatmentprocedure`.`relgrproc` = 'T'))));


03/08/2019
===========
1. XXXXXYYYYYZZZZChanged fp_callbacurl, fp_callbackurlfailure in urlproperties to https://www.mydentalpractice.in/my_pms2/payment/payment_success_hdfc

16/08/2019
==========
1. XXXXYYYYZZZ Added HDFC related fields in urlproperties
ALTER TABLE `mydp_stg`.`urlproperties` 
ADD COLUMN `hdfc_merchantid` VARCHAR(45) NULL DEFAULT NULL AFTER `encryption`,
ADD COLUMN `hdfc_account_name` VARCHAR(255) NULL DEFAULT NULL AFTER `hdfc_merchantid`,
ADD COLUMN `hdfc_test_domain` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_account_name`,
ADD COLUMN `hdfc_prod_domain` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_test_domain`,
ADD COLUMN `hdfc_access_code` VARCHAR(45) NULL DEFAULT NULL AFTER `hdfc_prod_domain`,
ADD COLUMN `hdfc_working_key` VARCHAR(45) NULL DEFAULT NULL AFTER `hdfc_access_code`,
ADD COLUMN `hdfc_return_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_working_key`,
ADD COLUMN `hdfc_cancel_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_return_url`,
ADD COLUMN `hdfc_getrsa_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_cancel_url`,
ADD COLUMN `hdfc_transaction_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_getrsa_url`,
ADD COLUMN `hdfc_json_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_transaction_url`,
ADD COLUMN `mydp_getrsa_url` VARCHAR(1024) NULL DEFAULT NULL AFTER `hdfc_json_url`;


21/08/2019
===========
1. XXXXYYYZZZZUpdate the following in URLPROPERTIES
XURL: https://rzp_live_4YNbY5bdhAuBbB:nIvCYme12MWsu9jsryEabfDO@api.razorpay.com/v1                                          (urlprops:fp_produrl, fp_testurl)
XMerchant Name: My Dental Healt Plan Pvt. Ltd.  (urlprops:fp_merchantdisplay  payment:fp_merchantdisplay)
XMerchant ID : D88Fg9JQZFspay                   (urlprops:fp_merchantid  payment:fp_merchantid)
API Key :              
Xkey_id :   rzp_live_4YNbY5bdhAuBbB(urlprops:fp_apikey)
Xkey_secret: nIvCYme12MWsu9jsryEabfDO(urlprops:fp_privatekey)

22/08/2019
==========
1. XXXXYYYYZZZModified Case Report table
ALTER TABLE `mydp_stg`.`casereport` 
ADD COLUMN `child_name` VARCHAR(128) NULL DEFAULT NULL AFTER `casereport`,
ADD COLUMN `child_class` VARCHAR(128) NULL DEFAULT NULL AFTER `child_name`,
ADD COLUMN `cavity_milk_teeth` CHAR(1) NULL DEFAULT 'F' AFTER `child_class`,
ADD COLUMN `cavity_perm_teeth` CHAR(1) NULL DEFAULT 'F' AFTER `cavity_milk_teeth`,
ADD COLUMN `crooked_teeth` CHAR(1) NULL DEFAULT 'F' AFTER `cavity_perm_teeth`,
ADD COLUMN `gum_problems` CHAR(1) NULL DEFAULT 'F' AFTER `crooked_teeth`,
ADD COLUMN `emergency_consult` CHAR(1) NULL DEFAULT 'F' AFTER `gum_problems`,
ADD COLUMN `priority_checkup` CHAR(1) NULL DEFAULT 'F' AFTER `emergency_consult`,
ADD COLUMN `routine_checkup` VARCHAR(45) NULL DEFAULT 'F' AFTER `priority_checkup`,
ADD COLUMN `image_file` VARCHAR(1024) NULL DEFAULT NULL AFTER `routine_checkup`;

ALTER TABLE `mydp_stg`.`casereport` 
ADD COLUMN `fluoride_check` CHAR(1) NULL DEFAULT 'F' AFTER `routine_checkup`;

ALTER TABLE `mydp_stg`.`casereport` 
ADD COLUMN `parent_name` VARCHAR(128) NULL DEFAULT NULL AFTER `child_name`,
ADD COLUMN `school_name` VARCHAR(128) NULL DEFAULT NULL AFTER `parent_name`,
ADD COLUMN `admission_number` VARCHAR(45) NULL DEFAULT NULL AFTER `school_name`,
ADD COLUMN `email` VARCHAR(128) NULL DEFAULT NULL AFTER `child_class`,
ADD COLUMN `dob` DATE NULL DEFAULT NULL AFTER `email`;


ALTER TABLE `mydp_stg`.`casereport` 
ADD COLUMN `cell` VARCHAR(45) NULL AFTER `child_class`;

ALTER TABLE `mydp_stg`.`casereport` 
ADD COLUMN `gender` CHAR(45) NULL DEFAULT 'Male' AFTER `dob`;


2. XXXXYYYYZZZZ vw_casereport
USE `mydp_stg`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_casereport` AS
    SELECT 
        `casereport`.`id` AS `id`,
        `casereport`.`providerid` AS `providerid`,
        `casereport`.`memberid` AS `memberid`,
        `casereport`.`patientid` AS `patientid`,
        `casereport`.`treatmentid` AS `treatmentid`,
        `casereport`.`appointmentid` AS `appointmentid`,
        `casereport`.`casereport` AS `casereport`,
        `casereport`.`child_name` AS `child_name`,
        `casereport`.`child_class` AS `child_class`,
        `casereport`.`parent_name` AS `parent_name`,
        `casereport`.`school_name` AS `school_name`,
        `casereport`.`admission_number` AS `admission_number`,
        `casereport`.`cell` AS `cell`,
        `casereport`.`email` AS `email`,
        `casereport`.`dob` AS `dob`,
        `casereport`.`gender` AS `gender`,
        `casereport`.`cavity_milk_teeth` AS `cavity_milk_teeth`,
        `casereport`.`cavity_perm_teeth` AS `cavity_perm_teeth`,
        `casereport`.`crooked_teeth` AS `crooked_teeth`,
        `casereport`.`gum_problems` AS `gum_problems`,
        `casereport`.`emergency_consult` AS `emergency_consult`,
        `casereport`.`priority_checkup` AS `priority_checkup`,
        `casereport`.`routine_checkup` AS `routine_checkup`,
        `casereport`.`fluoride_check` AS `fluoride_check`,
        `casereport`.`image_file` AS `image_file`,
        `doctor`.`name` AS `doctorname`,
        `provider`.`providername` AS `providername`,
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        `casereport`.`is_active` AS `is_active`,
        `casereport`.`modified_on` AS `modified_on`,
        `casereport`.`modified_by` AS `modified_by`
    FROM
        (((`casereport`
        LEFT JOIN `doctor` ON ((`casereport`.`doctorid` = `doctor`.`id`)))
        LEFT JOIN `provider` ON ((`casereport`.`providerid` = `provider`.`id`)))
        LEFT JOIN `vw_memberpatientlist` ON (((`casereport`.`memberid` = `vw_memberpatientlist`.`primarypatientid`)
            AND (`casereport`.`patientid` = `vw_memberpatientlist`.`patientid`))));

08/26/2019
===========

1. XXXXYYYZZZ created new table dentalcasesheet
CREATE TABLE `dentalcasesheet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providerid` int(11) DEFAULT NULL,
  `doctorid` int(11) DEFAULT NULL,
  `child_name` varchar(128) DEFAULT NULL,
  `parent_name` varchar(128) DEFAULT NULL,
  `school_name` varchar(128) DEFAULT NULL,
  `admission_number` varchar(45) DEFAULT NULL,
  `child_class` varchar(128) DEFAULT NULL,
  `cell` varchar(45) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` char(45) DEFAULT 'Male',
  `cavity_milk_teeth` char(1) DEFAULT 'F',
  `cavity_perm_teeth` char(1) DEFAULT 'F',
  `crooked_teeth` char(1) DEFAULT 'F',
  `gum_problems` char(1) DEFAULT 'F',
  `emergency_consult` char(1) DEFAULT 'F',
  `priority_checkup` char(1) DEFAULT 'F',
  `routine_checkup` varchar(45) DEFAULT 'F',
  `fluoride_check` char(1) DEFAULT 'F',
  `casereport` longtext,
  `image_file` varchar(1024) DEFAULT NULL,
  `is_active` char(1) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1536 DEFAULT CHARSET=utf8;


2. XXXXYYYYZZZZ created new view vw_dentalcasesheet
CREATE 
   
VIEW `vw_dentalcasesheet` AS
    SELECT 
        `dentalcasesheet`.`id` AS `id`,
        `dentalcasesheet`.`providerid` AS `providerid`,
        `dentalcasesheet`.`doctorid` AS `doctorid`,
        `dentalcasesheet`.`casereport` AS `casereport`,
        `dentalcasesheet`.`child_name` AS `child_name`,
        `dentalcasesheet`.`child_class` AS `child_class`,
        `dentalcasesheet`.`parent_name` AS `parent_name`,
        `dentalcasesheet`.`school_name` AS `school_name`,
        `dentalcasesheet`.`admission_number` AS `admission_number`,
        `dentalcasesheet`.`cell` AS `cell`,
        `dentalcasesheet`.`email` AS `email`,
        `dentalcasesheet`.`dob` AS `dob`,
        `dentalcasesheet`.`gender` AS `gender`,
        `dentalcasesheet`.`cavity_milk_teeth` AS `cavity_milk_teeth`,
        `dentalcasesheet`.`cavity_perm_teeth` AS `cavity_perm_teeth`,
        `dentalcasesheet`.`crooked_teeth` AS `crooked_teeth`,
        `dentalcasesheet`.`gum_problems` AS `gum_problems`,
        `dentalcasesheet`.`emergency_consult` AS `emergency_consult`,
        `dentalcasesheet`.`priority_checkup` AS `priority_checkup`,
        `dentalcasesheet`.`routine_checkup` AS `routine_checkup`,
        `dentalcasesheet`.`fluoride_check` AS `fluoride_check`,
        `dentalcasesheet`.`image_file` AS `image_file`,
        `doctor`.`name` AS `doctorname`,
        `provider`.`providername` AS `providername`,
        `dentalcasesheet`.`is_active` AS `is_active`
    FROM
        ((`dentalcasesheet`
        LEFT JOIN `doctor` ON ((`dentalcasesheet`.`doctorid` = `doctor`.`id`)))
        LEFT JOIN `provider` ON ((`dentalcasesheet`.`providerid` = `provider`.`id`)))

3. ZZZZ altered casereport

4. ZZZZ altered vw_casereport


08/28/2019
==========

1. XXXZZZZModified vw_memberpatientlist
USE `mydp_stg`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_memberpatientlist` AS
    SELECT 
        `patientmember`.`id` AS `id`,
        `patientmember`.`id` AS `patientid`,
        `patientmember`.`id` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'P' AS `patienttype`,
        `patientmember`.`title` AS `title`,
        `patientmember`.`fname` AS `fname`,
        `patientmember`.`lname` AS `lname`,
        CONCAT(IFNULL(`patientmember`.`fname`, ''),
                ' ',
                IFNULL(`patientmember`.`lname`, '')) AS `fullname`,
        CONCAT(IFNULL(`patientmember`.`fname`, ''),
                ' ',
                IFNULL(`patientmember`.`lname`, ''),
                ' :',
                IFNULL(`patientmember`.`patientmember`, '')) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(IFNULL(patientmember.patientmember,''),
                ' ',
                IFNULL(`patientmember`.`fname`, ''),
                ' ',
                IFNULL(`patientmember`.`mname`, ''),
                ' ',
                IFNULL(`patientmember`.`lname`, ''),
                '  ',
                IFNULL(`patientmember`.`cell`, ''),
                ' ',
                IFNULL(`patientmember`.`email`, '')) AS `pattern`,
        `patientmember`.`dob` AS `dob`,
        `patientmember`.`gender` AS `gender`,
        'Self' AS `relation`,
        `patientmember`.`image` AS `image`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmember`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmember`.`newmember` AS `newmember`,
        `patientmember`.`freetreatment` AS `freetreatment`,
        CAST((CASE
                WHEN ISNULL(`patientmember`.`dob`) THEN 0
                WHEN (YEAR(`patientmember`.`dob`) = 0) THEN 0
                ELSE ((YEAR(NOW()) * 1.0) - (YEAR(`patientmember`.`dob`) * 1.0))
            END)
            AS UNSIGNED) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        `vw_treatmentplancost`.`totaltreatmentcost` AS `totaltreatmentcost`,
        `vw_treatmentplancost`.`totalmemberpays` AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmember`
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
        LEFT JOIN `vw_treatmentplancost` ON ((`patientmember`.`id` = `vw_treatmentplancost`.`primarypatient`))) 
    UNION SELECT 
        `patientmemberdependants`.`id` AS `id`,
        `patientmemberdependants`.`id` AS `patientid`,
        `patientmemberdependants`.`patientmember` AS `primarypatientid`,
        `patientmember`.`patientmember` AS `patientmember`,
        `patientmember`.`groupref` AS `groupref`,
        'D' AS `patienttype`,
        `patientmemberdependants`.`title` AS `title`,
        `patientmemberdependants`.`fname` AS `fname`,
        `patientmemberdependants`.`lname` AS `lname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`) AS `fullname`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                ' :',
                `patientmember`.`patientmember`) AS `patient`,
        `patientmember`.`cell` AS `cell`,
        `patientmember`.`email` AS `email`,
        CONCAT(`patientmemberdependants`.`fname`,
                ' ',
                `patientmemberdependants`.`lname`,
                '  ',
                `patientmember`.`cell`,
                ' ',
                `patientmember`.`email`) AS `pattern`,
        `patientmemberdependants`.`depdob` AS `dob`,
        `patientmemberdependants`.`gender` AS `gender`,
        `patientmemberdependants`.`relation` AS `relation`,
        '' AS `image`,
        `patientmember`.`groupregion` AS `regionid`,
        `patientmember`.`provider` AS `providerid`,
        `patientmemberdependants`.`is_active` AS `is_active`,
        `patientmember`.`hmopatientmember` AS `hmopatientmember`,
        `patientmember`.`hmoplan` AS `hmoplan`,
        `patientmember`.`company` AS `company`,
        `patientmemberdependants`.`newmember` AS `newmember`,
        `patientmemberdependants`.`freetreatment` AS `freetreatment`,
        CAST((CASE
                WHEN ISNULL(`patientmemberdependants`.`depdob`) THEN 0
                WHEN (YEAR(`patientmemberdependants`.`depdob`) = 0) THEN 0
                ELSE ((YEAR(NOW()) * 1.0) - (YEAR(`patientmemberdependants`.`depdob`) * 1.0))
            END)
            AS UNSIGNED) AS `age`,
        CAST(`patientmember`.`premstartdt` AS DATE) AS `premstartdt`,
        CAST(`patientmember`.`premenddt` AS DATE) AS `premenddt`,
        `hmoplan`.`name` AS `hmoplanname`,
        `hmoplan`.`hmoplancode` AS `hmoplancode`,
        `hmoplan`.`procedurepriceplancode` AS `procedurepriceplancode`,
        0 AS `totaltreatmentcost`,
        0 AS `totaldue`,
        1 AS `created_by`,
        '2016-01-01' AS `created_on`,
        1 AS `modified_by`,
        '2016-01-01' AS `modified_on`
    FROM
        ((`patientmemberdependants`
        LEFT JOIN `patientmember` ON ((`patientmember`.`id` = `patientmemberdependants`.`patientmember`)))
        LEFT JOIN `hmoplan` ON ((`patientmember`.`hmoplan` = `hmoplan`.`id`)))
    ORDER BY `ID` DESC;

08/29/2019
==========

1. XXXZZZZurlproperties
ALTER TABLE `mydp_stg`.`urlproperties` 
ADD COLUMN `welcomekit` CHAR(1) NULL DEFAULT 'T' AFTER `mydp_getrsa_url`;

09/1/2019
==========

Gmail Server setting
--------------------
1. Update urlpropertis
update urlproperties set mailserverport = '587', mailsender = 'mydentalplan.in@gmail.com', 
mailusername = 'mydentalplan.in@gmail.com', mailpassword='MNgrak@7526#',
mailserver='smtp.gmail.com' where id = 1


Godaddy Settings
-----------------
update urlproperties set mailserverport = '587', mailsender = 'enrollment@mydentalplan.in', 
mailusername = 'enrollment@mydentalplan.in', mailpassword='enr0!!ment',
mailserver='p3plcpnl0607.prod.phx3.secureserver.net' where id = 1


09/09/2019
===========
1. XXXYYYZZZAdded DentalCaseSheet id in patientmember
ALTER TABLE `mydp_stg`.`patientmember` 
ADD COLUMN `dcsid` INT(11) 0 AFTER `freetreatment`;


10/14/2019
===========
1. XXXXYYYYZZZModify Company Add four payment flags for each company. By default they are all true 
ALTER TABLE `company` 
ADD COLUMN `onlinepayment` CHAR(1) NULL DEFAULT 'T' AFTER `authorizationrequired`,
ADD COLUMN `cashlesspayment` CHAR(1) NULL DEFAULT 'T' AFTER `onlinepayment`,
ADD COLUMN `cashpayment` CHAR(1) NULL DEFAULT 'T' AFTER `cashlesspayment`,
ADD COLUMN `chequepayment` CHAR(1) NULL DEFAULT 'T' AFTER `cashpayment`;


2. XXXXYYYZZZZAdd pagination in urlproperties
ALTER TABLE `urlproperties` 
ADD COLUMN `pagination` INT(11) NULL DEFAULT 10 AFTER `welcomekit`;


3. XXXXYYYZZZZCreat preregisterimage table

  CREATE TABLE `preregisterimage` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `preregisterid` int(11) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `imagedate` date DEFAULT NULL,
  `tooth` varchar(45) DEFAULT NULL,
  `quadrant` varchar(45) DEFAULT NULL,
  `description` longtext,
  `is_active` char(1) DEFAULT 'T',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


  
4. XXXXYYYYZZZModify preregister table
ALTER TABLE `preregister` 
ADD COLUMN `st` VARCHAR(45) NULL DEFAULT NULL AFTER `pin`,
ADD COLUMN `employeephoto` VARCHAR(255) NULL DEFAULT NULL AFTER `treatmentplandetails`,
ADD COLUMN `employeeid` VARCHAR(45) NULL DEFAULT NULL AFTER `employeephoto`,
ADD COLUMN `provider` INT(11) NULL DEFAULT NULL AFTER `company`,
ADD COLUMN `gender` VARCHAR(45) NULL DEFAULT 'Male' AFTER `st`,
ADD COLUMN `dob` DATE NULL DEFAULT NULL AFTER `gender`,

5. XXXXYYYYZZZModify medicalnotes
ALTER TABLE `medicalnotes` 
ADD COLUMN `height` VARCHAR(45) NULL DEFAULT NULL AFTER `occupation`,
ADD COLUMN `weight` VARCHAR(45) NULL DEFAULT NULL AFTER `height`;


25/12/2019
===========


1. XXXYYYYZZZZZNew Tables for MediAssist Claim form
CREATE TABLE `mediclaim` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `treatmentid` int(11) DEFAULT NULL,
  `tplanid` int(11) DEFAULT NULL,
  `companyid` int(11) DEFAULT NULL,
  `memberid` int(11) DEFAULT NULL,
  `patientid` int(11) DEFAULT NULL,
  `final_statement` char(1) DEFAULT 'F',
  `request_for_authorization` char(1) DEFAULT 'F',
  `preauth_number` varchar(45) DEFAULT NULL,
  `history` varchar(512) DEFAULT NULL,
  `allergy` varchar(512) DEFAULT NULL,
  `chiefcomplaint` varchar(128) DEFAULT NULL,
  `oralprophylate` char(1) DEFAULT 'F',
  `orthodontics` char(1) DEFAULT 'F',
  `remarks` text,
  `employeesignature` varchar(255) DEFAULT NULL,
  `employeesignaturedate` date DEFAULT NULL,
  `dentistsignature` varchar(255) DEFAULT NULL,
  `dentistsignaturedate` date DEFAULT NULL,
  `attendingdoctor` varchar(128) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `treatment_fk_idx` (`treatmentid`),
  KEY `tplan_fk_idx` (`tplanid`),
  KEY `company_fk_idx` (`companyid`),
  KEY `member_fk_idx` (`memberid`),
  KEY `patient_fk_idx` (`patientid`),
  CONSTRAINT `company_fk` FOREIGN KEY (`companyid`) REFERENCES `company` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `member_fk` FOREIGN KEY (`memberid`) REFERENCES `patientmember` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `patient_fk` FOREIGN KEY (`patientid`) REFERENCES `patientmember` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tplan_fk` FOREIGN KEY (`tplanid`) REFERENCES `treatmentplan` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `treatment_fk` FOREIGN KEY (`treatmentid`) REFERENCES `treatment` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



CREATE TABLE `mediclaim_procedures` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mediclaimid` int(11) DEFAULT NULL,
  `procedureid` int(11) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mediclaim_fk_idx` (`mediclaimid`),
  KEY `procedure_fk_idx` (`procedureid`),
  CONSTRAINT `mediclaim_fk` FOREIGN KEY (`mediclaimid`) REFERENCES `mediclaim` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `procedure_fk` FOREIGN KEY (`procedureid`) REFERENCES `dentalprocedure` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `mediclaim_attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mediclaimid` int(11) DEFAULT NULL,
  `attachment` varchar(512) DEFAULT NULL,
  `title` varchar(45) DEFAULT NULL,
  `description` text,
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mediclaim_fk_idx` (`mediclaimid`),
  CONSTRAINT `mediclaim_attach_fk` FOREIGN KEY (`mediclaimid`) REFERENCES `mediclaim` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `mediclaim_charts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mediclaimid` int(11) DEFAULT NULL,
  `restoration_ul_1` char(1) DEFAULT 'F',
  `restoration_ul_2` char(1) DEFAULT 'F',
  `restoration_ul_3` char(1) DEFAULT 'F',
  `restoration_ul_4` char(1) DEFAULT 'F',
  `restoration_ul_5` char(1) DEFAULT 'F',
  `restoration_ul_6` char(1) DEFAULT 'F',
  `restoration_ul_7` char(1) DEFAULT 'F',
  `restoration_ul_8` char(1) DEFAULT 'F',
  `restoration_ur_1` char(1) DEFAULT 'F',
  `restoration_ur_2` char(1) DEFAULT 'F',
  `restoration_ur_3` char(1) DEFAULT 'F',
  `restoration_ur_4` char(1) DEFAULT 'F',
  `restoration_ur_5` char(1) DEFAULT 'F',
  `restoration_ur_6` char(1) DEFAULT 'F',
  `restoration_ur_7` char(1) DEFAULT 'F',
  `restoration_ur_8` char(1) DEFAULT 'F',
  `restoration_ll_1` char(1) DEFAULT 'F',
  `restoration_ll_2` char(1) DEFAULT 'F',
  `restoration_ll_3` char(1) DEFAULT 'F',
  `restoration_ll_4` char(1) DEFAULT 'F',
  `restoration_ll_5` char(1) DEFAULT 'F',
  `restoration_ll_6` char(1) DEFAULT 'F',
  `restoration_ll_7` char(1) DEFAULT 'F',
  `restoration_ll_8` char(1) DEFAULT 'F',
  `restoration_lr_1` char(1) DEFAULT 'F',
  `restoration_lr_2` char(1) DEFAULT 'F',
  `restoration_lr_3` char(1) DEFAULT 'F',
  `restoration_lr_4` char(1) DEFAULT 'F',
  `restoration_lr_5` char(1) DEFAULT 'F',
  `restoration_lr_6` char(1) DEFAULT 'F',
  `restoration_lr_7` char(1) DEFAULT 'F',
  `restoration_lr_8` char(1) DEFAULT 'F',
  `rootcanal_ul_1` char(1) DEFAULT 'F',
  `rootcanal_ul_2` char(1) DEFAULT 'F',
  `rootcanal_ul_3` char(1) DEFAULT 'F',
  `rootcanal_ul_4` char(1) DEFAULT 'F',
  `rootcanal_ul_5` char(1) DEFAULT 'F',
  `rootcanal_ul_6` char(1) DEFAULT 'F',
  `rootcanal_ul_7` char(1) DEFAULT 'F',
  `rootcanal_ul_8` char(1) DEFAULT 'F',
  `rootcanal_ur_1` char(1) DEFAULT 'F',
  `rootcanal_ur_2` char(1) DEFAULT 'F',
  `rootcanal_ur_3` char(1) DEFAULT 'F',
  `rootcanal_ur_4` char(1) DEFAULT 'F',
  `rootcanal_ur_5` char(1) DEFAULT 'F',
  `rootcanal_ur_6` char(1) DEFAULT 'F',
  `rootcanal_ur_7` char(1) DEFAULT 'F',
  `rootcanal_ur_8` char(1) DEFAULT 'F',
  `rootcanal_ll_1` char(1) DEFAULT 'F',
  `rootcanal_ll_2` char(1) DEFAULT 'F',
  `rootcanal_ll_3` char(1) DEFAULT 'F',
  `rootcanal_ll_4` char(1) DEFAULT 'F',
  `rootcanal_ll_5` char(1) DEFAULT 'F',
  `rootcanal_ll_6` char(1) DEFAULT 'F',
  `rootcanal_ll_7` char(1) DEFAULT 'F',
  `rootcanal_ll_8` char(1) DEFAULT 'F',
  `rootcanal_lr_1` char(1) DEFAULT 'F',
  `rootcanal_lr_2` char(1) DEFAULT 'F',
  `rootcanal_lr_3` char(1) DEFAULT 'F',
  `rootcanal_lr_4` char(1) DEFAULT 'F',
  `rootcanal_lr_5` char(1) DEFAULT 'F',
  `rootcanal_lr_6` char(1) DEFAULT 'F',
  `rootcanal_lr_7` char(1) DEFAULT 'F',
  `rootcanal_lr_8` char(1) DEFAULT 'F',
  `extract_ul_1` char(1) DEFAULT 'F',
  `extract_ul_2` char(1) DEFAULT 'F',
  `extract_ul_3` char(1) DEFAULT 'F',
  `extract_ul_4` char(1) DEFAULT 'F',
  `extract_ul_5` char(1) DEFAULT 'F',
  `extract_ul_6` char(1) DEFAULT 'F',
  `extract_ul_7` char(1) DEFAULT 'F',
  `extract_ul_8` char(1) DEFAULT 'F',
  `extract_ur_1` char(1) DEFAULT 'F',
  `extract_ur_2` char(1) DEFAULT 'F',
  `extract_ur_3` char(1) DEFAULT 'F',
  `extract_ur_4` char(1) DEFAULT 'F',
  `extract_ur_5` char(1) DEFAULT 'F',
  `extract_ur_6` char(1) DEFAULT 'F',
  `extract_ur_7` char(1) DEFAULT 'F',
  `extract_ur_8` char(1) DEFAULT 'F',
  `extract_ll_1` char(1) DEFAULT 'F',
  `extract_ll_2` char(1) DEFAULT 'F',
  `extract_ll_3` char(1) DEFAULT 'F',
  `extract_ll_4` char(1) DEFAULT 'F',
  `extract_ll_5` char(1) DEFAULT 'F',
  `extract_ll_6` char(1) DEFAULT 'F',
  `extract_ll_7` char(1) DEFAULT 'F',
  `extract_ll_8` char(1) DEFAULT 'F',
  `extract_lr_1` char(1) DEFAULT 'F',
  `extract_lr_2` char(1) DEFAULT 'F',
  `extract_lr_3` char(1) DEFAULT 'F',
  `extract_lr_4` char(1) DEFAULT 'F',
  `extract_lr_5` char(1) DEFAULT 'F',
  `extract_lr_6` char(1) DEFAULT 'F',
  `extract_lr_7` char(1) DEFAULT 'F',
  `extract_lr_8` char(1) DEFAULT 'F',
  `missing_ul_1` char(1) DEFAULT 'F',
  `missing_ul_2` char(1) DEFAULT 'F',
  `missing_ul_3` char(1) DEFAULT 'F',
  `missing_ul_4` char(1) DEFAULT 'F',
  `missing_ul_5` char(1) DEFAULT 'F',
  `missing_ul_6` char(1) DEFAULT 'F',
  `missing_ul_7` char(1) DEFAULT 'F',
  `missing_ul_8` char(1) DEFAULT 'F',
  `missing_ur_1` char(1) DEFAULT 'F',
  `missing_ur_2` char(1) DEFAULT 'F',
  `missing_ur_3` char(1) DEFAULT 'F',
  `missing_ur_4` char(1) DEFAULT 'F',
  `missing_ur_5` char(1) DEFAULT 'F',
  `missing_ur_6` char(1) DEFAULT 'F',
  `missing_ur_7` char(1) DEFAULT 'F',
  `missing_ur_8` char(1) DEFAULT 'F',
  `missing_ll_1` char(1) DEFAULT 'F',
  `missing_ll_2` char(1) DEFAULT 'F',
  `missing_ll_3` char(1) DEFAULT 'F',
  `missing_ll_4` char(1) DEFAULT 'F',
  `missing_ll_5` char(1) DEFAULT 'F',
  `missing_ll_6` char(1) DEFAULT 'F',
  `missing_ll_7` char(1) DEFAULT 'F',
  `missing_ll_8` char(1) DEFAULT 'F',
  `missing_lr_1` char(1) DEFAULT 'F',
  `missing_lr_2` char(1) DEFAULT 'F',
  `missing_lr_3` char(1) DEFAULT 'F',
  `missing_lr_4` char(1) DEFAULT 'F',
  `missing_lr_5` char(1) DEFAULT 'F',
  `missing_lr_6` char(1) DEFAULT 'F',
  `missing_lr_7` char(1) DEFAULT 'F',
  `missing_lr_8` char(1) DEFAULT 'F',
  `xray_ul_1` char(1) DEFAULT 'F',
  `xray_ul_2` char(1) DEFAULT 'F',
  `xray_ul_3` char(1) DEFAULT 'F',
  `xray_ul_4` char(1) DEFAULT 'F',
  `xray_ul_5` char(1) DEFAULT 'F',
  `xray_ul_6` char(1) DEFAULT 'F',
  `xray_ul_7` char(1) DEFAULT 'F',
  `xray_ul_8` char(1) DEFAULT 'F',
  `xray_ur_1` char(1) DEFAULT 'F',
  `xray_ur_2` char(1) DEFAULT 'F',
  `xray_ur_3` char(1) DEFAULT 'F',
  `xray_ur_4` char(1) DEFAULT 'F',
  `xray_ur_5` char(1) DEFAULT 'F',
  `xray_ur_6` char(1) DEFAULT 'F',
  `xray_ur_7` char(1) DEFAULT 'F',
  `xray_ur_8` char(1) DEFAULT 'F',
  `xray_ll_1` char(1) DEFAULT 'F',
  `xray_ll_2` char(1) DEFAULT 'F',
  `xray_ll_3` char(1) DEFAULT 'F',
  `xray_ll_4` char(1) DEFAULT 'F',
  `xray_ll_5` char(1) DEFAULT 'F',
  `xray_ll_6` char(1) DEFAULT 'F',
  `xray_ll_7` char(1) DEFAULT 'F',
  `xray_ll_8` char(1) DEFAULT 'F',
  `xray_lr_1` char(1) DEFAULT 'F',
  `xray_lr_2` char(1) DEFAULT 'F',
  `xray_lr_3` char(1) DEFAULT 'F',
  `xray_lr_4` char(1) DEFAULT 'F',
  `xray_lr_5` char(1) DEFAULT 'F',
  `xray_lr_6` char(1) DEFAULT 'F',
  `xray_lr_7` char(1) DEFAULT 'F',
  `xray_lr_8` char(1) DEFAULT 'F',
  `is_active` char(1) DEFAULT 'T',
  `created_by` int(11) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `modified_by` int(11) DEFAULT NULL,
  `modified_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mediclaim_charts_fk_idx` (`mediclaimid`),
  CONSTRAINT `mediclaim_charts_fk` FOREIGN KEY (`mediclaimid`) REFERENCES `mediclaim` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

2. XXXXYYYYYZZZZZImportProvider table
ALTER TABLE `mydp_stg`.`importprovider` 
ADD COLUMN `bankname` VARCHAR(128) NULL DEFAULT NULL AFTER `region`,
ADD COLUMN `bankbranch` VARCHAR(128) NULL DEFAULT NULL AFTER `bankname`,
ADD COLUMN `bankaccountno` VARCHAR(45) NULL DEFAULT NULL AFTER `bankbranch`,
ADD COLUMN `bankaccounttype` VARCHAR(45) NULL DEFAULT NULL AFTER `bankaccountno`,
ADD COLUMN `bankmicro` VARCHAR(45) NULL DEFAULT NULL AFTER `bankaccounttype`,
ADD COLUMN `bankifscode` VARCHAR(45) NULL DEFAULT NULL AFTER `bankmicro`,
ADD COLUMN `latitude` VARCHAR(45) NULL DEFAULT NULL AFTER `bankifscode`,
ADD COLUMN `longitude` VARCHAR(45) NULL DEFAULT NULL AFTER `latitude`,
ADD COLUMN `locationurl` VARCHAR(45) NULL DEFAULT NULL AFTER `longtitude`;

3. XXXXYYYZZZZModify Provider
ALTER TABLE `mydp_stg`.`provider` 
CHANGE COLUMN `practicename` `practicename` VARCHAR(515) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_longtitude` `pa_longitude` VARCHAR(128) NULL DEFAULT NULL ;

4. XXXYYYZZZZNeed to install 'haversine' package
If pip install fails, then copy haversine folder from local/staging to production
python27/Lib/site-pacakges


26/12/2019
===========

1. XXXYYYZZZModify Provider Bank
Add columnn providerid


13/01/2020
==========
1. XXXYYYZZZZModify vw_relgrtreatmentprocedure
2. role & role_default in db.py
3. speciality & speciality_default in db.py
4.XXXYYYZZZAdded 'speciality'
ALTER TABLE `mydp_stg`.`provider` 
ADD COLUMN `speciality` INT(11) NULL DEFAULT NULL AFTER `languagesspoken`;
5. XXXYYYZZZAdded specialityid column in speciality
ALTER TABLE `mydp_stg`.`speciality` 
ADD COLUMN `specialityid` INT(11) NULL AFTER `id`;
6. XXXYYYZZZAdded roleid col in role
ALTER TABLE `mydp_stg`.`role` 
ADD COLUMN `roleid` INT(11) NULL AFTER `id`;

7.XXXYYYZZZ
UPDATE speciality t1 
        INNER JOIN speciality_default t2 
             ON t1.speciality = t2.speciality
SET t1.specialityid = t2.id

UPDATE role t1 
        INNER JOIN role_default t2 
             ON t1.role = t2.role
SET t1.roleid = t2.id

UPDATE doctor t1 
        INNER JOIN role t2 
             ON t1.role = t2.id
SET t1.role = t2.roleid;

UPDATE doctor t1 
        INNER JOIN speciality t2 
             ON t1.speciality = t2.id
SET t1.speciality = t2.specialityid

8. XXXYYYZZZadded is_active, created_on, created_by, modified_on, modified_by fields in role_default & speciality_default

ALTER TABLE speciality_default` 
ADD COLUMN `is_active` CHAR(1) NULL DEFAULT 'T' AFTER `speciality`,
ADD COLUMN `created_by` INT(11) NULL AFTER `is_active`,
ADD COLUMN `created_on` DATETIME NULL AFTER `created_by`,
ADD COLUMN `modified_by` INT(11) NULL AFTER `created_on`,
ADD COLUMN `modified_on` DATETIME NULL AFTER `modified_by`;

9. XXXXYYYZZZAlter role_default table to make primary key 'id' as AUto Increment

10.XXXYYYZZZ alter provider to change lenght of some fields
ALTER TABLE `mydp_stg`.`provider` 
CHANGE COLUMN `providername` `providername` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `practicename` `practicename` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `address1` `address1` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `address2` `address2` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `address3` `address3` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address1` `p_address1` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address2` `p_address2` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `p_address3` `p_address3` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_providername` `pa_providername` VARCHAR(512) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_practicename` `pa_practicename` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_practiceaddress` `pa_practiceaddress` VARCHAR(512) NULL DEFAULT NULL ,
CHANGE COLUMN `pa_address` `pa_address` VARCHAR(512) NULL DEFAULT NULL ;


10. XXXXYYYZZZZModif vw_relgrtreatmentprocedure
USE `mydp_stg`;
CREATE 
     OR REPLACE ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `vw_relgrtreatmentprocedure` AS
    SELECT 
        `vw_memberpatientlist`.`fullname` AS `fullname`,
        `vw_memberpatientlist`.`cell` AS `cell`,
        `vw_memberpatientlist`.`groupref` AS `groupref`,
        `vw_memberpatientlist`.`patientmember` AS `patientmember`,
        company.company AS company,
        `rlgprovider`.`providerid` AS `providerid`,
        `rlgprovider`.`providercode` AS `providercode`,
        `provider`.`pa_providername` AS `providername`,
        `provider`.`pa_practicename` AS `practicename`,
        `provider`.`pa_regno` AS `regno`,
        `provider`.`pa_practiceaddress` AS `practiceaddress`,
        `vw_treatmentprocedure`.`treatment` AS `treatment`,
        `vw_treatmentprocedure`.`treatmentdate` AS `treatmentdate`,
        `vw_treatmentprocedure`.`service_id` AS `service_id`,
        `vw_treatmentprocedure`.`procedurecode` AS `procedurecode`,
        `vw_treatmentprocedure`.`altshortdescription` AS `procdesc`,
        `vw_treatmentprocedure`.`procedurefee` AS `procedurefee`,
        `vw_treatmentprocedure`.`copay` AS `copay`,
        `vw_treatmentprocedure`.`inspays` AS `inspays`,
        `vw_treatmentprocedure`.`tooth` AS `tooth`,
        `vw_treatmentprocedure`.`quadrant` AS `quadrant`,
        `vw_treatmentprocedure`.`relgrprocdesc` AS `relgrprocdesc`,
        `vw_treatmentprocedure`.`relgrproc` AS `relgrproc`,
        `vw_treatmentprocedure`.`status` AS `status`,
        `vw_treatmentprocedure`.`is_active` AS `is_active`,
        `vw_treatmentprocedure`.`relgrtransactionid` AS `relgrtransactionid`
    FROM
        (((`rlgprovider`
        LEFT JOIN `provider` ON ((`provider`.`id` = `rlgprovider`.`providerid`)))
        LEFT JOIN `vw_treatmentprocedure` ON (((`vw_treatmentprocedure`.`providerid` = `rlgprovider`.`providerid`)
            AND (`vw_treatmentprocedure`.`relgrproc` = 'T'))))
        LEFT JOIN `vw_memberpatientlist` ON (((`vw_memberpatientlist`.`primarypatientid` = `vw_treatmentprocedure`.`primarypatient`)
            AND (`vw_memberpatientlist`.`patientid` = `vw_treatmentprocedure`.`patient`))))
		LEFT JOIN company on (company.id = vw_memberpatientlist.company);


9. XXXXYYYZZZZCreate ImportDoctor
CREATE TABLE `importdoctor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(45) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  `provider` varchar(128) DEFAULT NULL,
  `speciality` varchar(128) DEFAULT NULL,
  `role` varchar(128) DEFAULT NULL,
  `practice_owner` char(1) DEFAULT 'f',
  `email` varchar(128) DEFAULT NULL,
  `cell` varchar(45) DEFAULT NULL,
  `registration` varchar(45) DEFAULT NULL,
  `color` varchar(45) DEFAULT NULL,
  `stafftype` varchar(45) DEFAULT NULL,
  `docsms` char(1) DEFAULT 'T',
  `docemail` char(1) DEFAULT 'T',
  `groupsms` char(1) DEFAULT 'F',
  `groupemail` char(1) DEFAULT 'F',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=611 DEFAULT CHARSET=utf8;


ALTER TABLE `mydp_stg`.`importdoctor` 
ADD COLUMN `providerid` INT(11) NULL AFTER `groupemail`,
ADD COLUMN `specialityid` INT(11) NULL AFTER `providerid`,
ADD COLUMN `roleid` INT(11) NULL AFTER `specialityid`;

24/02/2020
===========

1. XXXYYYZZZZCreated RLGVOUCHER table
CREATE TABLE `mydp_stg`.`rlgvoucher` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `vouchercode` VARCHAR(10) NULL DEFAULT NULL,
  `fname` VARCHAR(128) NULL DEFAULT NULL,
  `mname` VARCHAR(128) NULL DEFAULT NULL,
  `lname` VARCHAR(128) NULL DEFAULT NULL,
  `cell` VARCHAR(45) NULL,
  `dob` DATE NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_by` INT(11) NULL DEFAULT NULL,
  `created_on` DATETIME NULL DEFAULT NULL,
  `modified_by` INT(11) NULL DEFAULT NULL,
  `modified_on` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`));
ALTER TABLE `mydp_stg`.`rlgvoucher` 
ADD COLUMN `plancode` VARCHAR(45) NULL DEFAULT NULL AFTER `id`;

XXXYYYYZZZZAdded columns policy, cell, gender, dob

2. XXXXYYYYZZZZCreated importrlgvoucher
CREATE TABLE `mydp_stg`.`importrlgvoucher` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `plancode` VARCHAR(45) NULL DEFAULT NULL,
  `policy` VARCHAR(45) NULL DEFAULT NULL,
  `vouchercode` VARCHAR(45) NULL DEFAULT NULL,
  `fname` VARCHAR(128) NULL DEFAULT NULL,
  `mname` VARCHAR(128) NULL DEFAULT NULL,
  `lname` VARCHAR(128) NULL DEFAULT NULL,
  PRIMARY KEY (`id`));

3. ----YYYYYZZZZCREATE TABLE `mydp_stg`.`rlgplanprovider` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `providerid` INT(11) NULL,
  `policy` VARCHAR(45) NULL,
  `planid` INT(11) NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  PRIMARY KEY (`id`));

4. XXXYYYZZZAdd Plan RLG399 in HMOPLAN

5. ----YYYZZZZPopulte rlgplanprovider

6. ----Need to wirte utility to populate rlgplanprovider for all religare providers

7. XXXYYYZZZCREATE TABLE `provider_region_plan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providercode` varchar(45) DEFAULT NULL,
  `companycode` varchar(45) DEFAULT NULL,
  `regioncode` varchar(45) DEFAULT NULL,
  `policy` varchar(45) DEFAULT NULL,
  `plancode` varchar(45) DEFAULT NULL,
  `is_active` char(1) DEFAULT 'T',
  `created_by` varchar(45) DEFAULT NULL,
  `created_on` int(11) DEFAULT NULL,
  `modified_by` varchar(45) DEFAULT NULL,
  `modified_on` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;


8. XXXYYYZZZCREATE TABLE `mydp_stg`.`sessionlog` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `promocode` VARCHAR(45) NULL DEFAULT NULL,
  `ackid` VARCHAR(45) NULL DEFAULT NULL,
  `is_active` CHAR(1) NULL DEFAULT 'T',
  `created_by` INT(11) NULL DEFAULT NULL,
  `created_on` DATETIME NULL DEFAULT NULL,
  `modified_by` INT(11) NULL DEFAULT NULL,
  `modified_on` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`));

9.XXXXYYYZZZZImport Provider Region Plan.
CREATE TABLE `import_provider_region_plan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `providercode` varchar(45) DEFAULT NULL,
  `companycode` varchar(45) DEFAULT NULL,
  `regioncode` varchar(45) DEFAULT NULL,
  `policy` varchar(45) DEFAULT NULL,
  `plancode` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

10. Need to populate provider_region_plan plan using import utility

11. ----YYYYZZZZDrop table rlgplanprovider

12/03/2020
==========
0. XXXYYYZZZAdded import_provider_region_plan  table

1. XXXYYYYAdded procedurepriceplancode

ALTER TABLE `mydp_stg`.`provider_region_plan` 
ADD COLUMN `procedurepriceplancode` VARCHAR(45) NULL DEFAULT NULL AFTER `plancode`;

2. Populate provider_region_plan table for Colgate2000


3. SELECT patientmember.company,company.company,patientmember.groupregion,groupregion.groupregion,patientmember.hmoplan,hmoplan.hmoplancode FROM mydp_stg.patientmember 
LEFT JOIN company on company.id = patientmember.company
LEFT JOIN groupregion on groupregion.id = patientmember.groupregion
LEFT JOIN hmoplan on hmoplan.id = patientmember.hmoplan
group by patientmember.company,patientmember.groupregion, patientmember.hmoplan


8/04/2020
==========

1.  XXXYYZZReligare Properties 
CREATE TABLE `rlgproperties` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `policy_name` varchar(256) DEFAULT NULL,
  `api_key` varchar(45) DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;


2, XXXYYZZrlgdocument
ALTER TABLE `mydp_prod`.`rlgdocument` 
ADD COLUMN `policy_name` VARCHAR(45) NULL AFTER `policy_number`,
ADD COLUMN `voucher_code` VARCHAR(45) NULL AFTER `customer_id`;

3. XXXYYZZmodified import provider_region_plan to Populate provider_region_plan procedurepriceplancode

4. YYZZPopulate procedure fee in procedurepriceplan 

5. XXXYYYZZZALTER TABLE `mydp_prod`.`treatment_procedure` 
ADD COLUMN `policy_name` VARCHAR(128) NULL DEFAULT NULL AFTER `service_id`;

24/07/2020
===========
1. Copy PHP files from myphp folder into inetpub/wwwroot
2. modify http://myphp.com/ to http://localhost// in encrypt & decrypt functions

23/8/2020
==========
1. XXXZZZZModify vw_relgrtreatmentprocedure  adding GST
2. XXXZZZCreated RLGDC company
3. XXXZZZimported RLGDC

11/9/2020
==========
1. YYYYZZZZAdd ABHICL errorr messages in rlgerrormessage table
2. XXXYYYZZZAdd ABHICL Company
3. XXXYYYZZZAdd ABHILC Plan
4. XXXImport ProcedurePricePlan for ABHICL
5. XXXmport provider_regions_plan for ABHIC
6. XXXXYYYYZZZZmodify vw_treatmentlist - added companyid, groupref, patientmember, enddate,description/notes,tooth,quadrant,
7. XXXYYYYZZZZmodify vw_appointments - added "companyid" & "groupref", "membercode"
8.


4/11/2020
==========
1.XXXYYYZZZZcreate ratelimint table
CREATE TABLE `mydp_prod`.`ratelimit` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NULL,
  `lastlogin` DATETIME NULL,
  `created_by` INT(11) NULL,
  `created_on` DATETIME NULL,
  `modified_by` INT(11) NULL,
  `modified_on` DATETIME NULL,
  PRIMARY KEY (`id`));


11/29/2020
===XX=======
1. XXXYYYZZCreate Customer table
2. XXYYYZZCreate vw_customer

12/3/2020
=========
1. XXXYYYZZZModified dentalimage table. Added uploadfolder

12/6/2020
=========
1. YYYZZZAdded Media table 'media'
2. XXYYYZZZmodified activity tracker table

12/15/2020
==========
1. XXXYYZZZadded vw_customertopcount
2. XXXYYYZZZadded vw_customerdetailcount

12/17/2020
==========
1. YYYZZZModified media with dicom fields
ALTER TABLE `mydp_prod`.`media` 
ADD COLUMN `dicomUserUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `modified_by`,
ADD COLUMN `dicomAcctUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomUserUuid`,
ADD COLUMN `dicomInstUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomAcctUuid`,
ADD COLUMN `dicomPatName` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomInstUuid`,
ADD COLUMN `dicomPatUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatName`,
ADD COLUMN `dicomPatid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatUuid`,
ADD COLUMN `dicomPatOrderUuid` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatid`,
ADD COLUMN `dicomProcDesc` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomPatOrderUuid`,
ADD COLUMN `dicomPerformedDate` VARCHAR(128) NULL DEFAULT NULL AFTER `dicomProcDesc`,
ADD COLUMN `dicomURL` VARCHAR(255) NULL DEFAULT NULL AFTER `dicomPerformedDate`,
ADD COLUMN `mediacol` VARCHAR(45) NULL AFTER `dicomURL`;

2. YYZZTransfer dentalimage -> Media
   copy all files from uploads folder to media\image\MDP_PROV\MDP_Member
3. YYZZrun this SQL script by changing the uploadfolder
   insert into media (title,media,uploadfolder,tooth,quadrant,
mediadate,description,treatmentplan,treatment,
patientmember,patient,patienttype,patientname,provider,
mediatype,mediaformat,
dicomUserUuid, dicomAcctUuid, dicomInstUuid,
dicomPatName,dicomPatUuid,dicomPatid, dicomPatOrderUuid,
dicomProcDesc, dicomPerformedDate,dicomURL,
is_active,created_on,created_by,modified_on,modified_by)
SELECT title,image,"c:\\inetpub\\wwwroot\\media\\image\\MDP_PROV\\MDP_MEMBER",
tooth,quadrant,imagedate,
description,treatmentplan,treatment,patientmember,patient,
patienttype,patientname,provider,'Image','jpg',
dicomUserUuid, dicomAcctUuid, dicomInstUuid,
dicomPatName,dicomPatUuid,dicomPatid, dicomPatOrderUuid,
dicomProcDesc, dicomPerformedDate,dicomURL,
is_active,created_on,created_by,modified_on,modified_by
from dentalimage

12/20/2020
===========
1. XXXXYYYZZModify dentalimage table
   ALTER TABLE `mydp_prod`.`dentalimage` 
ADD COLUMN `mediafile` VARCHAR(1024) NULL DEFAULT NULL AFTER `treatmentplan`,
ADD COLUMN `mediatype` VARCHAR(45) NULL DEFAULT 'audio' AFTER `mediafile`,
ADD COLUMN `mediaformat` VARCHAR(45) NULL DEFAULT 'mp3' AFTER `mediatype`,
ADD COLUMN `mediasize` DOUBLE NULL DEFAULT '0' AFTER `mediaformat`;

12/28/2020
===========
1. XXXYYYZZZAdd CustomerDependants
2. XXXYYZZZAdd view Customer Dependants

1/16/2021
=========
0. XXYZRenamed old Media to xmedia
1. XXYZRemove Media, xMedia, DentalImage_1
2. XYZNew dentlaimage_ref

1. XYZNew - Clinic,clinic_ref   (need to add owner flag in Clinic)

3. XYZNew - ops_timing,ops_timing_ref


5. XYZNew - doctor_ref

7. XYZNew - bank_details

8  XYZModify Provider to add Provider status   varchar(45),, modify foreign key constraint of providerbank

9.  XYZNew -  prospect, prospect_ref,

10. XYZNew activity_log, activity_log_ref

11. XYZNew travel_log, travel_log_ref

12. XYZmigrate providerbank to bank_details;

truncate bank_details;

INSERT INTO bank_details(providerid,bankname,bankbranch,bankaccountno,bankaccounttype,bankmicrno,bankifsccode)
SELECT providerid,bankname,bankbranch,bankaccountno,bankaccounttype,bankmicrno,bankifsccode FROM providerbank;

UPDATE provider AS p INNER JOIN bank_details AS b ON p.id = b.providerid SET p.bankid = b.id


5/2/2021
=========

1. XXXXYYYZZZvw_prescription_groupby_treattment
2. XYZZZZvw_procedure_groupby_treatment
3. XYZZZZvw_abhicl_report_group
4. XYZZZvw_abhicl_report


07/2/2021
==========

1. XYYZZModified t_appointment : added 'clinicid' field, set default value of blockappt = False, delete foreign keys provider and patient
2. XXYYZZModified vw_appointments : added clinicid, clinic_ref and clinic_name fields
3. XXYYZZModified clinic table : added state_dental_regisration, registration_certificate

15/2/2021
=========
1. XXYYYYZZAdded CustomerActivity table

26/2/2021
=========
1. XXXZZZAdded gender & dob in Prospect table
2. XXXZZZAdded 'notes' field in Clinic table

8/3/2021
========
1. XXXYYYZZAdded Clinic ID for this treatment
2. XXYYZZAdded clinicid, clinicname to vw_treatmentlist
2. ZZZCreate and Assign clinic to Provider & Treatments by running assign clinic utility


19/3/2021
=========
1. XXXYYZZAdded DOB & Gender in vw_appointments
2. XXXYYYZZZ New importSPAT table

7/4/2021
========
1. XXXYYYZZZZNew Booking table
2. XXXYYYYZZZZCreate & Populate package_region_plan
3. XXXYYYZZZUpdate dentalimage uploadfolder
XXXYYYZZZupdate dentalimage set uploadfolder = 'c:\\inetpub\\wwwroot\\applications\\my_pms2\\uploads' where id <= 467

XXXZZZupdate speciality in doctor to refer to speciality_default
XXXZZZZupdate role in doctor to refer to role_default

21/4/2021
=========
1. XXXYYYZZZrole_default,  set role = 'Office_Staff' instead of Office Boy

28/4/202
========
1. XXXYYYZZZZCreate ImportSAPTProv table

30/04/2021
==========
1. XXXYYYZZZconsentform table

5/5/2021
========
1. XXYYYZZZModified Patientmember - added imageid
2. XXXYYYZZZModified Provider - added imageid

5/8/2021
=========
1. XXXYYYZZZ Create new vw_clinic

5/10/2021
==========
1. XXXYYYZZZadd is_active flag in medicine_default 
2. XXXXYYYZZZmodify medicine_default strngthuom to strengthuom
3. XXXYYYZZZadd imageid col in doctor table

5/22/2021
=========
1. XXXYYYZZZNew tables for Cities & States
2. XXXYYYZZZAdded field 'newcity' in prospects table
3. XXXXYYYYZZZAdded hmopatientmember in vw_appointments
4, XXXXYYYZZZZadding clinicid to vw_appointment* views
5. XXXXYYYZZZ vw_patientprescription
6. XXXYYYZZZZNew Table Shopsee Properties to add SHOPSEE specific 
CREATE TABLE `shopsee_properties` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shopsee_stg_url` varchar(512) DEFAULT NULL,
  `shopsee_prod_url` varchar(512) DEFAULT NULL,
  `shopsee_api_token` varchar(512) DEFAULT NULL,
  `shopsee_response_key` varchar(512) DEFAULT NULL,
  `shopsee_axis_db_card` varchar(45) DEFAULT NULL,
  `shopsee_axis_cr_card` varchar(45) DEFAULT NULL,
  `shopsee_hdfc_db_card` varchar(45) DEFAULT NULL,
  `shopsee_axis_db_card_exp` varchar(45) DEFAULT NULL,
  `shopsee_axis_db_card_cvv` varchar(45) DEFAULT NULL,
  `shopsee_axis_db_card_otp` varchar(45) DEFAULT NULL,
  `shopsee_axis_cr_card_exp` varchar(45) DEFAULT NULL,
  `shopsee_axis_cr_card_cvv` varchar(45) DEFAULT NULL,
  `shopsee_axis_cr_card_otp` varchar(45) DEFAULT NULL,
  `shopsee_hdfc_db_card_exp` varchar(45) DEFAULT NULL,
  `shopsee_hdfc_db_card_cvv` varchar(45) DEFAULT NULL,
  `shopsee_hdfc_db_card_otp` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
ALTER TABLE `mydp_prod`.`shopsee_properties` 
ADD COLUMN `shopsee_url` VARCHAR(512) NULL DEFAULT NULL AFTER `id`,
ADD COLUMN `shopsee_returnURL` VARCHAR(512) NULL DEFAULT NULL AFTER `shopsee_url`;


7. XXXXYYYYZZZZAdded longitude & latitude fileds in clinic table


8. XXXXYYYZZZ Add IND_IS_SYNC in auth_user
ALTER TABLE `mydp_prod`.`auth_user` 
ADD COLUMN `IND_IS_SYNC` CHAR(1) NULL DEFAULT NULL AFTER `impersonatorlname`;

9. XXXXYYYZZZ Add IND_VC in provider
ALTER TABLE `mydp_prod`.`provider` 
ADD COLUMN `IND_VC` CHAR(1) NULL DEFAULT 'F' AFTER `imageid`;

10 XXXXYYYYZZZ Add IND_IS_SYNCH
ALTER TABLE `mydp_prod`.`doctor` 
ADD COLUMN `IND_IS_SYNC` CHAR(1) NULL AFTER `modified_on`;

11. XXXXYYYZZZ vw_doctor (IND_IS_SYNC)

12. XXXXYYYYZZZ vw_provider (IND_VC)

13. XXXXYYYZZZ added col IND_IS_SYNC in Company table
ALTER TABLE `mydp_prod`.`company` 
ADD COLUMN `IND_IS_SYNC` CHAR(1) NULL AFTER `chequepayment`;


24/06/2021
===========
1. XXXYYYZZZZAdd Product Name & Product ID fields Shopsee Properties
ALTER TABLE `mydp_prod`.`shopsee_properties` 
ADD COLUMN `product_name` VARCHAR(512) NULL DEFAULT NULL AFTER `shopsee_hdfc_db_card_otp`,
ADD COLUMN `product_id` VARCHAR(512) NULL DEFAULT NULL AFTER `product_name`;

2.XXXXYYYYZZZZAdd webHookUrl
ALTER TABLE `mydp_prod`.`shopsee_properties` 
ADD COLUMN `webhookUrl` VARCHAR(512) NULL DEFAULT NULL AFTER `product_id`;




10/07/2021
===========

1. XXXYYYZZZAdded tables benefit_master, benefit_master_x_plan,benefit_master_x_message,benefit_master_x_slabs,benefit_member,benefit_messages,benefit_redeem_slabs,benefit_member_x_benfit_master

2. XXXXYYYZZZModified Customer table by adding 'clinicid'

3. XXXXYYYYZZZdelete benefit_message, benefit_master_x_message

4. XXXXYYYZZZAdd mdpmessages table (populate)

19/07/2021
=============
1. XXXYYZZZ modified vw_clinic : addd latitude & longitude

2. XXXYYYZZZ modified benefit_master : added benefit_premium  

3. YYYYZZZZmodified customer table to add payment related information - tx_id, payment_id, payment_amount, payment_date,amount_paid, payment_status

22/07/2021
===========
1. Modify treatmentplan table to add totalcompanypays

2. Modify payment table to add companypays,policy

3. Modify vw_paymentlist,vw_payments,vw_treatmentplancost,vw_treatmentplansummarybypatient,vw_treatmentplansummarybytreatment

4. New Table company_policy



Script file to clear user for sign-up
=====================================

9035314080 9741628429 7014405827

SELECT * FROM mydp_prod.auth_user where cell = '7014405827'
SELECT * FROM mydp_prod.agent where cell = '7014405827'
SELECT * FROM mydp_prod.provider where cell = '7014405827'
SELECT * FROM mydp_prod.prospect where  cell = '7014405827'
SELECT * FROM mydp_prod.clinic where cell = '7014405827'
SELECT * FROM mydp_prod.patientmember where cell = '7014405827'
SELECT * FROM mydp_prod.webmember where cell = '7014405827'
select * from doctor where cell = '7014405827'
9916314080
SELECT * FROM mydp_prod.auth_user where cell = '7062559946'
SELECT * FROM mydp_prod.agent where cell = '7062559946'
SELECT * FROM mydp_prod.provider where cell = '7062559946'
SELECT * FROM mydp_prod.prospect where  cell = '7062559946'
SELECT * FROM mydp_prod.clinic where cell = '7062559946'
SELECT * FROM mydp_prod.patientmember where cell = '7062559946'
SELECT * FROM mydp_prod.webmember where cell = '7062559946'
select * from doctor where cell = '7062559946'

SELECT * FROM mydp_prod.auth_user where cell = '9035314080'
SELECT * FROM mydp_prod.agent where cell = '9035314080'
SELECT * FROM mydp_prod.provider where cell = '9035314080'
SELECT * FROM mydp_prod.prospect where  cell = '9035314080'
SELECT * FROM mydp_prod.clinic where cell = '9035314080'
SELECT * FROM mydp_prod.patientmember where cell = '9035314080'
SELECT * FROM mydp_prod.webmember where cell = '9035314080'
select * from doctor where cell = '9035314080'

select * from prospect order by id desc
select * from clinic order by id desc
select * from clinic_ref order by id desc
select * from provider order by id desc
select * from doctor order by id desc
select * from doctor_ref order by id desc

select * from patientmember order by id desc

SELECT * FROM mydp_prod.auth_user where cell = '9741628429'
SELECT * FROM mydp_prod.agent where cell = '9741628429'
SELECT * FROM mydp_prod.provider where cell = '9741628429'
SELECT * FROM mydp_prod.prospect where  cell = '9741628429'
SELECT * FROM mydp_prod.clinic where cell = '9741628429'
SELECT * FROM mydp_prod.patientmember where cell = '9741628429'
SELECT * FROM mydp_prod.webmember where cell = '9741628429'
select * from doctor where cell = '9741628429'
SELECT * FROM mydp_prod.webmember where webmember = 'P00019249'


9035314080 9741628429 7014405827
update auth_user set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update provider set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update prospect set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update patientmember set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update webmember set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update clinic set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
update doctor set cell = concat(id,cell) , email = concat(id,email) where cell = '7239962886 ';
manjunathshidling1@gmail.com
SELECT * FROM mydp_prod.auth_user where cell = '9035314080'
SELECT * FROM mydp_prod.agent where cell = '9035314080'
SELECT * FROM mydp_prod.provider where cell = '9035314080'
SELECT * FROM mydp_prod.prospect where  cell = '9035314080'
SELECT * FROM mydp_prod.clinic where cell = '9035314080'
SELECT * FROM mydp_prod.patientmember where cell = '9035314080'
SELECT * FROM mydp_prod.webmember where cell = '9035314080'