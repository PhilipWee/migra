alter type "public"."v2" owner to session_user;

alter view "public"."v2" owner to session_user;

alter type "public"."v" owner to session_user;

alter view "public"."v" owner to session_user;

drop view if exists "public"."v2";

alter type "public"."v" owner to schemainspect_test_role2;

alter view "public"."v" owner to schemainspect_test_role2;