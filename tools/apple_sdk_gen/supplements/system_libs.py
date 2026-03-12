"""Generate TBD stubs for public system libraries in usr/lib/.

These stubs allow linking against system libraries like ``-lz``,
``-lsqlite3``, ``-lxml2``, etc.  Symbol lists are extracted from
the Xcode iOS SDK and embedded here so the tool works without Xcode.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ── Public C/C++ library definitions ──────────────────────────────
# Each tuple: (tbd_name, install_name, aliases, symbols)
# aliases are unversioned names that re-export the versioned lib.

_LIBZ_1_SYMS = (
    "_adler32 _adler32_combine _adler32_z _compress _compress2 _compressBound _crc32"
    "_crc32_combine _crc32_combine_gen _crc32_combine_op _crc32_z _deflate _deflateBound"
    "_deflateCopy _deflateEnd _deflateGetDictionary _deflateInit2_ _deflateInit_ _deflateParams"
    "_deflatePending _deflatePrime _deflateReset _deflateResetKeep _deflateSetDictionary"
    "_deflateSetHeader _deflateTune _get_crc_table _gzbuffer _gzclearerr _gzclose _gzclose_r"
    "_gzclose_w _gzdirect _gzdopen _gzeof _gzerror _gzflush _gzfread _gzfwrite _gzgetc _gzgetc_"
    "_gzgets _gzoffset _gzopen _gzprintf _gzputc _gzputs _gzread _gzrewind _gzseek _gzsetparams"
    "_gztell _gzungetc _gzvprintf _gzwrite _inflate _inflateBack _inflateBackEnd"
    "_inflateBackInit_ _inflateCodesUsed _inflateCopy _inflateEnd _inflateGetDictionary"
    "_inflateGetHeader _inflateInit2_ _inflateInit_ _inflateMark _inflatePrime _inflateReset"
    "_inflateReset2 _inflateResetKeep _inflateSetDictionary _inflateSync _inflateSyncPoint"
    "_inflateUndermine _inflateValidate _uncompress _uncompress2 _zError _zlibCompileFlags"
    "_zlibVersion"
).split()

_LIBSQLITE3_SYMS = (
    "__sqlite3_apple_archive __sqlite3_apple_archive_type __sqlite3_apple_unarchive"
    "__sqlite3_db_clone __sqlite3_db_copy __sqlite3_db_copy_compact __sqlite3_db_truncate"
    "__sqlite3_integrity_check __sqlite3_lockstate __sqlite3_maintain_load_factor"
    "__sqlite3_purgeEligiblePagerCacheMemory __sqlite3_system_busy_handler"
    "__sqlite_auto_profile __sqlite_auto_trace _sqlite3_activate_see _sqlite3_aggregate_context"
    "_sqlite3_aggregate_count _sqlite3_auto_extension _sqlite3_autovacuum_pages"
    "_sqlite3_backup_finish _sqlite3_backup_init _sqlite3_backup_pagecount"
    "_sqlite3_backup_remaining _sqlite3_backup_step _sqlite3_bind_blob _sqlite3_bind_blob64"
    "_sqlite3_bind_blob_b _sqlite3_bind_double _sqlite3_bind_int _sqlite3_bind_int64"
    "_sqlite3_bind_null _sqlite3_bind_parameter_count _sqlite3_bind_parameter_index"
    "_sqlite3_bind_parameter_name _sqlite3_bind_pointer _sqlite3_bind_text _sqlite3_bind_text16"
    "_sqlite3_bind_text64 _sqlite3_bind_text_b _sqlite3_bind_value _sqlite3_bind_zeroblob"
    "_sqlite3_bind_zeroblob64 _sqlite3_blob_bytes _sqlite3_blob_close _sqlite3_blob_open"
    "_sqlite3_blob_read _sqlite3_blob_reopen _sqlite3_blob_write _sqlite3_busy_handler"
    "_sqlite3_busy_timeout _sqlite3_cancel_auto_extension _sqlite3_carray_bind"
    "_sqlite3_carray_init _sqlite3_changes _sqlite3_changes64 _sqlite3_clear_bindings"
    "_sqlite3_close _sqlite3_close_v2 _sqlite3_collation_needed _sqlite3_collation_needed16"
    "_sqlite3_column_blob _sqlite3_column_bytes _sqlite3_column_bytes16 _sqlite3_column_count"
    "_sqlite3_column_database_name _sqlite3_column_database_name16 _sqlite3_column_decltype"
    "_sqlite3_column_decltype16 _sqlite3_column_double _sqlite3_column_int"
    "_sqlite3_column_int64 _sqlite3_column_name _sqlite3_column_name16"
    "_sqlite3_column_origin_name _sqlite3_column_origin_name16 _sqlite3_column_table_name"
    "_sqlite3_column_table_name16 _sqlite3_column_text _sqlite3_column_text16"
    "_sqlite3_column_type _sqlite3_column_value _sqlite3_commit_hook _sqlite3_compileoption_get"
    "_sqlite3_compileoption_used _sqlite3_complete _sqlite3_complete16 _sqlite3_config"
    "_sqlite3_context_db_handle _sqlite3_create_collation _sqlite3_create_collation16"
    "_sqlite3_create_collation_v2 _sqlite3_create_filename _sqlite3_create_function"
    "_sqlite3_create_function16 _sqlite3_create_function_v2 _sqlite3_create_module"
    "_sqlite3_create_module_v2 _sqlite3_create_window_function _sqlite3_csv_init"
    "_sqlite3_data_count _sqlite3_data_directory _sqlite3_database_file_object"
    "_sqlite3_db_cacheflush _sqlite3_db_config _sqlite3_db_filename _sqlite3_db_handle"
    "_sqlite3_db_mutex _sqlite3_db_name _sqlite3_db_readonly _sqlite3_db_release_memory"
    "_sqlite3_db_status _sqlite3_declare_vtab _sqlite3_deserialize _sqlite3_drop_modules"
    "_sqlite3_enable_shared_cache _sqlite3_errcode _sqlite3_errmsg _sqlite3_errmsg16"
    "_sqlite3_error_offset _sqlite3_errstr _sqlite3_exec _sqlite3_exec_b _sqlite3_expanded_sql"
    "_sqlite3_expired _sqlite3_extended_errcode _sqlite3_extended_result_codes"
    "_sqlite3_file_control _sqlite3_filename_database _sqlite3_filename_journal"
    "_sqlite3_filename_wal _sqlite3_finalize _sqlite3_free _sqlite3_free_filename"
    "_sqlite3_free_table _sqlite3_get_autocommit _sqlite3_get_auxdata _sqlite3_get_clientdata"
    "_sqlite3_get_table _sqlite3_global_recover _sqlite3_hard_heap_limit64 _sqlite3_initialize"
    "_sqlite3_intarray_bind _sqlite3_intarray_create _sqlite3_interrupt _sqlite3_is_interrupted"
    "_sqlite3_key _sqlite3_key_v2 _sqlite3_keyword_check _sqlite3_keyword_count"
    "_sqlite3_keyword_name _sqlite3_last_insert_rowid _sqlite3_libversion"
    "_sqlite3_libversion_number _sqlite3_limit _sqlite3_log _sqlite3_malloc _sqlite3_malloc64"
    "_sqlite3_memory_alarm _sqlite3_memory_highwater _sqlite3_memory_used _sqlite3_mprintf"
    "_sqlite3_msize _sqlite3_mutex_alloc _sqlite3_mutex_enter _sqlite3_mutex_free"
    "_sqlite3_mutex_leave _sqlite3_mutex_try _sqlite3_next_stmt _sqlite3_normalized_sql"
    "_sqlite3_open _sqlite3_open16 _sqlite3_open_v2 _sqlite3_os_end _sqlite3_os_init"
    "_sqlite3_overload_function _sqlite3_prepare _sqlite3_prepare16 _sqlite3_prepare16_v2"
    "_sqlite3_prepare16_v3 _sqlite3_prepare_v2 _sqlite3_prepare_v3 _sqlite3_preupdate_blobwrite"
    "_sqlite3_preupdate_count _sqlite3_preupdate_depth _sqlite3_preupdate_hook"
    "_sqlite3_preupdate_new _sqlite3_preupdate_old _sqlite3_profile _sqlite3_progress_handler"
    "_sqlite3_randomness _sqlite3_realloc _sqlite3_realloc64 _sqlite3_rekey _sqlite3_rekey_v2"
    "_sqlite3_release_memory _sqlite3_reset _sqlite3_reset_auto_extension _sqlite3_result_blob"
    "_sqlite3_result_blob64 _sqlite3_result_double _sqlite3_result_error"
    "_sqlite3_result_error16 _sqlite3_result_error_code _sqlite3_result_error_nomem"
    "_sqlite3_result_error_toobig _sqlite3_result_int _sqlite3_result_int64"
    "_sqlite3_result_null _sqlite3_result_pointer _sqlite3_result_subtype _sqlite3_result_text"
    "_sqlite3_result_text16 _sqlite3_result_text16be _sqlite3_result_text16le"
    "_sqlite3_result_text64 _sqlite3_result_value _sqlite3_result_zeroblob"
    "_sqlite3_result_zeroblob64 _sqlite3_rollback_hook _sqlite3_rtree_geometry_callback"
    "_sqlite3_rtree_query_callback _sqlite3_serialize _sqlite3_set_authorizer"
    "_sqlite3_set_auxdata _sqlite3_set_clientdata _sqlite3_set_last_insert_rowid"
    "_sqlite3_setlk_timeout _sqlite3_shutdown _sqlite3_sleep _sqlite3_snapshot_cmp"
    "_sqlite3_snapshot_free _sqlite3_snapshot_get _sqlite3_snapshot_open"
    "_sqlite3_snapshot_recover _sqlite3_snprintf _sqlite3_soft_heap_limit"
    "_sqlite3_soft_heap_limit64 _sqlite3_sourceid _sqlite3_sql _sqlite3_status"
    "_sqlite3_status64 _sqlite3_step _sqlite3_stmt_busy _sqlite3_stmt_explain"
    "_sqlite3_stmt_isexplain _sqlite3_stmt_readonly _sqlite3_stmt_scanstatus"
    "_sqlite3_stmt_scanstatus_reset _sqlite3_stmt_scanstatus_v2 _sqlite3_stmt_status"
    "_sqlite3_str_append _sqlite3_str_appendall _sqlite3_str_appendchar _sqlite3_str_appendf"
    "_sqlite3_str_errcode _sqlite3_str_finish _sqlite3_str_length _sqlite3_str_new"
    "_sqlite3_str_reset _sqlite3_str_value _sqlite3_str_vappendf _sqlite3_strglob"
    "_sqlite3_stricmp _sqlite3_strlike _sqlite3_strnicmp _sqlite3_system_errno"
    "_sqlite3_table_column_metadata _sqlite3_temp_directory _sqlite3_test_control"
    "_sqlite3_thread_cleanup _sqlite3_threadsafe _sqlite3_total_changes"
    "_sqlite3_total_changes64 _sqlite3_trace _sqlite3_trace_v2 _sqlite3_transfer_bindings"
    "_sqlite3_txn_state _sqlite3_update_hook _sqlite3_uri_boolean _sqlite3_uri_int64"
    "_sqlite3_uri_key _sqlite3_uri_parameter _sqlite3_user_data _sqlite3_value_blob"
    "_sqlite3_value_bytes _sqlite3_value_bytes16 _sqlite3_value_double _sqlite3_value_dup"
    "_sqlite3_value_encoding _sqlite3_value_free _sqlite3_value_frombind _sqlite3_value_int"
    "_sqlite3_value_int64 _sqlite3_value_nochange _sqlite3_value_numeric_type"
    "_sqlite3_value_pointer _sqlite3_value_subtype _sqlite3_value_text _sqlite3_value_text16"
    "_sqlite3_value_text16be _sqlite3_value_text16le _sqlite3_value_type _sqlite3_version"
    "_sqlite3_vfs_find _sqlite3_vfs_register _sqlite3_vfs_unregister _sqlite3_vmprintf"
    "_sqlite3_vsnprintf _sqlite3_vtab_collation _sqlite3_vtab_config _sqlite3_vtab_distinct"
    "_sqlite3_vtab_in _sqlite3_vtab_in_first _sqlite3_vtab_in_next _sqlite3_vtab_nochange"
    "_sqlite3_vtab_on_conflict _sqlite3_vtab_rhs_value _sqlite3_wal_autocheckpoint"
    "_sqlite3_wal_checkpoint _sqlite3_wal_checkpoint_v2 _sqlite3_wal_hook"
    "_sqlite3changegroup_add _sqlite3changegroup_add_change _sqlite3changegroup_add_strm"
    "_sqlite3changegroup_delete _sqlite3changegroup_new _sqlite3changegroup_output"
    "_sqlite3changegroup_output_strm _sqlite3changegroup_schema _sqlite3changeset_apply"
    "_sqlite3changeset_apply_strm _sqlite3changeset_apply_v2 _sqlite3changeset_apply_v2_strm"
    "_sqlite3changeset_concat _sqlite3changeset_concat_strm _sqlite3changeset_conflict"
    "_sqlite3changeset_finalize _sqlite3changeset_fk_conflicts _sqlite3changeset_invert"
    "_sqlite3changeset_invert_strm _sqlite3changeset_new _sqlite3changeset_next"
    "_sqlite3changeset_old _sqlite3changeset_op _sqlite3changeset_pk _sqlite3changeset_start"
    "_sqlite3changeset_start_strm _sqlite3changeset_start_v2 _sqlite3changeset_start_v2_strm"
    "_sqlite3rebaser_configure _sqlite3rebaser_create _sqlite3rebaser_delete"
    "_sqlite3rebaser_rebase _sqlite3rebaser_rebase_strm _sqlite3session_attach"
    "_sqlite3session_changeset _sqlite3session_changeset_size _sqlite3session_changeset_strm"
    "_sqlite3session_config _sqlite3session_create _sqlite3session_delete _sqlite3session_diff"
    "_sqlite3session_enable _sqlite3session_indirect _sqlite3session_isempty"
    "_sqlite3session_memory_used _sqlite3session_object_config _sqlite3session_patchset"
    "_sqlite3session_patchset_strm _sqlite3session_table_filter"
).split()

_LIBXML2_2_SYMS = (
    "_UTF8ToHtml _UTF8Toisolat1 ___docbDefaultSAXHandler ___htmlDefaultSAXHandler"
    "___oldXMLWDcompatibility ___xmlBufferAllocScheme ___xmlDefaultBufferSize"
    "___xmlDefaultSAXHandler ___xmlDefaultSAXLocator ___xmlDeregisterNodeDefaultValue"
    "___xmlDoValidityCheckingDefaultValue ___xmlGenericError ___xmlGenericErrorContext"
    "___xmlGetWarningsDefaultValue ___xmlIndentTreeOutput ___xmlKeepBlanksDefaultValue"
    "___xmlLastError ___xmlLineNumbersDefaultValue ___xmlLoadExtDtdDefaultValue"
    "___xmlOutputBufferCreateFilename ___xmlOutputBufferCreateFilenameValue"
    "___xmlParserDebugEntities ___xmlParserInputBufferCreateFilename"
    "___xmlParserInputBufferCreateFilenameValue ___xmlParserVersion"
    "___xmlPedanticParserDefaultValue ___xmlRegisterNodeDefaultValue ___xmlSaveNoEmptyTags"
    "___xmlStructuredError ___xmlStructuredErrorContext ___xmlSubstituteEntitiesDefaultValue"
    "___xmlTreeIndentString _attribute _attributeDecl _cdataBlock _characters _checkNamespace"
    "_comment _docbCreateFileParserCtxt _docbCreatePushParserCtxt _docbDefaultSAXHandler"
    "_docbDefaultSAXHandlerInit _docbEncodeEntities _docbFreeParserCtxt _docbParseChunk"
    "_docbParseDoc _docbParseDocument _docbParseFile _docbSAXParseDoc _docbSAXParseFile"
    "_elementDecl _endDocument _endElement _entityDecl _externalSubset _getColumnNumber"
    "_getEntity _getLineNumber _getNamespace _getParameterEntity _getPublicId _getSystemId"
    "_globalNamespace _hasExternalSubset _hasInternalSubset _htmlAttrAllowed _htmlAutoCloseTag"
    "_htmlCreateFileParserCtxt _htmlCreateMemoryParserCtxt _htmlCreatePushParserCtxt"
    "_htmlCtxtReadDoc _htmlCtxtReadFd _htmlCtxtReadFile _htmlCtxtReadIO _htmlCtxtReadMemory"
    "_htmlCtxtReset _htmlCtxtUseOptions _htmlDefaultSAXHandler _htmlDefaultSAXHandlerInit"
    "_htmlDocContentDumpFormatOutput _htmlDocContentDumpOutput _htmlDocDump _htmlDocDumpMemory"
    "_htmlDocDumpMemoryFormat _htmlElementAllowedHere _htmlElementStatusHere"
    "_htmlEncodeEntities _htmlEntityLookup _htmlEntityValueLookup _htmlFreeParserCtxt"
    "_htmlGetMetaEncoding _htmlHandleOmittedElem _htmlInitAutoClose _htmlIsAutoClosed"
    "_htmlIsBooleanAttr _htmlIsScriptAttribute _htmlNewDoc _htmlNewDocNoDtD _htmlNewParserCtxt"
    "_htmlNodeDump _htmlNodeDumpFile _htmlNodeDumpFileFormat _htmlNodeDumpFormatOutput"
    "_htmlNodeDumpOutput _htmlNodeStatus _htmlParseCharRef _htmlParseChunk _htmlParseDoc"
    "_htmlParseDocument _htmlParseElement _htmlParseEntityRef _htmlParseFile _htmlReadDoc"
    "_htmlReadFd _htmlReadFile _htmlReadIO _htmlReadMemory _htmlSAXParseDoc _htmlSAXParseFile"
    "_htmlSaveFile _htmlSaveFileEnc _htmlSaveFileFormat _htmlSetMetaEncoding _htmlTagLookup"
    "_ignorableWhitespace _initGenericErrorDefaultFunc _initdocbDefaultSAXHandler"
    "_inithtmlDefaultSAXHandler _initxmlDefaultSAXHandler _inputPop _inputPush _internalSubset"
    "_isStandalone _isolat1ToUTF8 _namePop _namePush _namespaceDecl _nodePop _nodePush"
    "_notationDecl _oldXMLWDcompatibility _processingInstruction _reference _resolveEntity"
    "_setDocumentLocator _setNamespace _startDocument _startElement _unparsedEntityDecl"
    "_valuePop _valuePush _xlinkGetDefaultDetect _xlinkGetDefaultHandler _xlinkIsLink"
    "_xlinkSetDefaultDetect _xlinkSetDefaultHandler _xmlACatalogAdd _xmlACatalogDump"
    "_xmlACatalogRemove _xmlACatalogResolve _xmlACatalogResolvePublic _xmlACatalogResolveSystem"
    "_xmlACatalogResolveURI _xmlAddAttributeDecl _xmlAddChild _xmlAddChildList _xmlAddDocEntity"
    "_xmlAddDtdEntity _xmlAddElementDecl _xmlAddEncodingAlias _xmlAddID _xmlAddNextSibling"
    "_xmlAddNotationDecl _xmlAddPrevSibling _xmlAddRef _xmlAddSibling _xmlAllocOutputBuffer"
    "_xmlAllocParserInputBuffer _xmlAttrSerializeTxtContent _xmlAutomataCompile"
    "_xmlAutomataGetInitState _xmlAutomataIsDeterminist _xmlAutomataNewAllTrans"
    "_xmlAutomataNewCountTrans _xmlAutomataNewCountTrans2 _xmlAutomataNewCountedTrans"
    "_xmlAutomataNewCounter _xmlAutomataNewCounterTrans _xmlAutomataNewEpsilon"
    "_xmlAutomataNewNegTrans _xmlAutomataNewOnceTrans _xmlAutomataNewOnceTrans2"
    "_xmlAutomataNewState _xmlAutomataNewTransition _xmlAutomataNewTransition2"
    "_xmlAutomataSetFinalState _xmlBoolToText _xmlBufContent _xmlBufEnd _xmlBufGetNodeContent"
    "_xmlBufNodeDump _xmlBufShrink _xmlBufUse _xmlBufferAdd _xmlBufferAddHead"
    "_xmlBufferAllocScheme _xmlBufferCCat _xmlBufferCat _xmlBufferContent _xmlBufferCreate"
    "_xmlBufferCreateSize _xmlBufferCreateStatic _xmlBufferDetach _xmlBufferDump"
    "_xmlBufferEmpty _xmlBufferFree _xmlBufferGrow _xmlBufferLength _xmlBufferResize"
    "_xmlBufferSetAllocationScheme _xmlBufferShrink _xmlBufferWriteCHAR _xmlBufferWriteChar"
    "_xmlBufferWriteQuotedString _xmlBuildQName _xmlBuildRelativeURI _xmlBuildURI"
    "_xmlByteConsumed _xmlC14NDocDumpMemory _xmlC14NDocSave _xmlC14NDocSaveTo _xmlC14NExecute"
    "_xmlCanonicPath _xmlCatalogAdd _xmlCatalogAddLocal _xmlCatalogCleanup _xmlCatalogConvert"
    "_xmlCatalogDump _xmlCatalogFreeLocal _xmlCatalogGetDefaults _xmlCatalogGetPublic"
    "_xmlCatalogGetSystem _xmlCatalogIsEmpty _xmlCatalogLocalResolve _xmlCatalogLocalResolveURI"
    "_xmlCatalogRemove _xmlCatalogResolve _xmlCatalogResolvePublic _xmlCatalogResolveSystem"
    "_xmlCatalogResolveURI _xmlCatalogSetDebug _xmlCatalogSetDefaultPrefer"
    "_xmlCatalogSetDefaults _xmlCharEncCloseFunc _xmlCharEncFirstLine _xmlCharEncInFunc"
    "_xmlCharEncOutFunc _xmlCharInRange _xmlCharStrdup _xmlCharStrndup _xmlCheckFilename"
    "_xmlCheckHTTPInput _xmlCheckLanguageID _xmlCheckUTF8 _xmlCheckVersion"
    "_xmlChildElementCount _xmlCleanupCharEncodingHandlers _xmlCleanupEncodingAliases"
    "_xmlCleanupGlobals _xmlCleanupInputCallbacks _xmlCleanupMemory _xmlCleanupOutputCallbacks"
    "_xmlCleanupParser _xmlCleanupPredefinedEntities _xmlCleanupThreads _xmlClearNodeInfoSeq"
    "_xmlClearParserCtxt _xmlConvertSGMLCatalog _xmlCopyAttributeTable _xmlCopyChar"
    "_xmlCopyCharMultiByte _xmlCopyDoc _xmlCopyDocElementContent _xmlCopyDtd"
    "_xmlCopyElementContent _xmlCopyElementTable _xmlCopyEntitiesTable _xmlCopyEnumeration"
    "_xmlCopyError _xmlCopyNamespace _xmlCopyNamespaceList _xmlCopyNode _xmlCopyNodeList"
    "_xmlCopyNotationTable _xmlCopyProp _xmlCopyPropList _xmlCreateDocParserCtxt"
    "_xmlCreateEntitiesTable _xmlCreateEntityParserCtxt _xmlCreateEnumeration"
    "_xmlCreateFileParserCtxt _xmlCreateIOParserCtxt _xmlCreateIntSubset"
    "_xmlCreateMemoryParserCtxt _xmlCreatePushParserCtxt _xmlCreateURI _xmlCreateURLParserCtxt"
    "_xmlCtxtGetLastError _xmlCtxtReadDoc _xmlCtxtReadFd _xmlCtxtReadFile _xmlCtxtReadIO"
    "_xmlCtxtReadMemory _xmlCtxtReset _xmlCtxtResetLastError _xmlCtxtResetPush"
    "_xmlCtxtUseOptions _xmlCurrentChar _xmlDOMWrapAdoptNode _xmlDOMWrapCloneNode"
    "_xmlDOMWrapFreeCtxt _xmlDOMWrapNewCtxt _xmlDOMWrapReconcileNamespaces"
    "_xmlDOMWrapRemoveNode _xmlDebugCheckDocument _xmlDebugDumpAttr _xmlDebugDumpAttrList"
    "_xmlDebugDumpDTD _xmlDebugDumpDocument _xmlDebugDumpDocumentHead _xmlDebugDumpEntities"
    "_xmlDebugDumpNode _xmlDebugDumpNodeList _xmlDebugDumpOneNode _xmlDebugDumpString"
    "_xmlDecodeEntities _xmlDefaultBufferSize _xmlDefaultSAXHandler _xmlDefaultSAXHandlerInit"
    "_xmlDefaultSAXLocator _xmlDelEncodingAlias _xmlDeregisterNodeDefault"
    "_xmlDeregisterNodeDefaultValue _xmlDetectCharEncoding _xmlDictCleanup _xmlDictCreate"
    "_xmlDictCreateSub _xmlDictExists _xmlDictFree _xmlDictGetUsage _xmlDictLookup _xmlDictOwns"
    "_xmlDictQLookup _xmlDictReference _xmlDictSetLimit _xmlDictSize"
    "_xmlDoValidityCheckingDefaultValue _xmlDocCopyNode _xmlDocCopyNodeList _xmlDocDump"
    "_xmlDocDumpFormatMemory _xmlDocDumpFormatMemoryEnc _xmlDocDumpMemory _xmlDocDumpMemoryEnc"
    "_xmlDocFormatDump _xmlDocGetRootElement _xmlDocSetRootElement _xmlDumpAttributeDecl"
    "_xmlDumpAttributeTable _xmlDumpElementDecl _xmlDumpElementTable _xmlDumpEntitiesTable"
    "_xmlDumpEntityDecl _xmlDumpNotationDecl _xmlDumpNotationTable _xmlElemDump"
    "_xmlEncodeEntities _xmlEncodeEntitiesReentrant _xmlEncodeSpecialChars _xmlErrMemory"
    "_xmlFileClose _xmlFileMatch _xmlFileOpen _xmlFileRead _xmlFindCharEncodingHandler"
    "_xmlFirstElementChild _xmlFree _xmlFreeAttributeTable _xmlFreeAutomata _xmlFreeCatalog"
    "_xmlFreeDoc _xmlFreeDocElementContent _xmlFreeDtd _xmlFreeElementContent"
    "_xmlFreeElementTable _xmlFreeEntitiesTable _xmlFreeEnumeration _xmlFreeIDTable"
    "_xmlFreeInputStream _xmlFreeMutex _xmlFreeNode _xmlFreeNodeList _xmlFreeNotationTable"
    "_xmlFreeNs _xmlFreeNsList _xmlFreeParserCtxt _xmlFreeParserInputBuffer _xmlFreePattern"
    "_xmlFreePatternList _xmlFreeProp _xmlFreePropList _xmlFreeRMutex _xmlFreeRefTable"
    "_xmlFreeStreamCtxt _xmlFreeTextReader _xmlFreeTextWriter _xmlFreeURI _xmlFreeValidCtxt"
    "_xmlGcMemGet _xmlGcMemSetup _xmlGenericError _xmlGenericErrorContext"
    "_xmlGetBufferAllocationScheme _xmlGetCharEncodingHandler _xmlGetCharEncodingName"
    "_xmlGetCompressMode _xmlGetDocCompressMode _xmlGetDocEntity _xmlGetDtdAttrDesc"
    "_xmlGetDtdElementDesc _xmlGetDtdEntity _xmlGetDtdNotationDesc _xmlGetDtdQAttrDesc"
    "_xmlGetDtdQElementDesc _xmlGetEncodingAlias _xmlGetExternalEntityLoader _xmlGetFeature"
    "_xmlGetFeaturesList _xmlGetGlobalState _xmlGetID _xmlGetIntSubset _xmlGetLastChild"
    "_xmlGetLastError _xmlGetLineNo _xmlGetNoNsProp _xmlGetNodePath _xmlGetNsList _xmlGetNsProp"
    "_xmlGetParameterEntity _xmlGetPredefinedEntity _xmlGetProp _xmlGetRefs _xmlGetThreadId"
    "_xmlGetUTF8Char _xmlGetWarningsDefaultValue _xmlHandleEntity _xmlHasFeature _xmlHasNsProp"
    "_xmlHasProp _xmlHashAddEntry _xmlHashAddEntry2 _xmlHashAddEntry3 _xmlHashCopy"
    "_xmlHashCreate _xmlHashCreateDict _xmlHashDefaultDeallocator _xmlHashFree _xmlHashLookup"
    "_xmlHashLookup2 _xmlHashLookup3 _xmlHashQLookup _xmlHashQLookup2 _xmlHashQLookup3"
    "_xmlHashRemoveEntry _xmlHashRemoveEntry2 _xmlHashRemoveEntry3 _xmlHashScan _xmlHashScan3"
    "_xmlHashScanFull _xmlHashScanFull3 _xmlHashSize _xmlHashUpdateEntry _xmlHashUpdateEntry2"
    "_xmlHashUpdateEntry3 _xmlIOFTPClose _xmlIOFTPMatch _xmlIOFTPOpen _xmlIOFTPRead"
    "_xmlIOHTTPClose _xmlIOHTTPMatch _xmlIOHTTPOpen _xmlIOHTTPOpenW _xmlIOHTTPRead"
    "_xmlIOParseDTD _xmlIndentTreeOutput _xmlInitCharEncodingHandlers _xmlInitGlobals"
    "_xmlInitMemory _xmlInitNodeInfoSeq _xmlInitParser _xmlInitParserCtxt _xmlInitThreads"
    "_xmlInitializeCatalog _xmlInitializeDict _xmlInitializeGlobalState"
    "_xmlInitializePredefinedEntities _xmlIsBaseChar _xmlIsBaseCharGroup _xmlIsBlank"
    "_xmlIsBlankNode _xmlIsChar _xmlIsCharGroup _xmlIsCombining _xmlIsCombiningGroup"
    "_xmlIsDigit _xmlIsDigitGroup _xmlIsExtender _xmlIsExtenderGroup _xmlIsID _xmlIsIdeographic"
    "_xmlIsIdeographicGroup _xmlIsLetter _xmlIsMainThread _xmlIsMixedElement _xmlIsPubidChar"
    "_xmlIsPubidChar_tab _xmlIsRef _xmlIsXHTML _xmlKeepBlanksDefault _xmlKeepBlanksDefaultValue"
    "_xmlLastElementChild _xmlLastError _xmlLineNumbersDefault _xmlLineNumbersDefaultValue"
    "_xmlLinkGetData _xmlListAppend _xmlListClear _xmlListCopy _xmlListCreate _xmlListDelete"
    "_xmlListDup _xmlListEmpty _xmlListEnd _xmlListFront _xmlListInsert _xmlListMerge"
    "_xmlListPopBack _xmlListPopFront _xmlListPushBack _xmlListPushFront _xmlListRemoveAll"
    "_xmlListRemoveFirst _xmlListRemoveLast _xmlListReverse _xmlListReverseSearch"
    "_xmlListReverseWalk _xmlListSearch _xmlListSize _xmlListSort _xmlListWalk _xmlLoadACatalog"
    "_xmlLoadCatalog _xmlLoadCatalogs _xmlLoadExtDtdDefaultValue _xmlLoadExternalEntity"
    "_xmlLoadSGMLSuperCatalog _xmlLockLibrary _xmlLsCountNode _xmlLsOneNode _xmlMalloc"
    "_xmlMallocAtomic _xmlMallocAtomicLoc _xmlMallocLoc _xmlMemBlocks _xmlMemDisplay"
    "_xmlMemDisplayLast _xmlMemFree _xmlMemGet _xmlMemMalloc _xmlMemRealloc _xmlMemSetup"
    "_xmlMemShow _xmlMemSize _xmlMemStrdup _xmlMemStrdupLoc _xmlMemUsed _xmlMemoryDump"
    "_xmlMemoryStrdup _xmlModuleClose _xmlModuleFree _xmlModuleOpen _xmlModuleSymbol"
    "_xmlMutexLock _xmlMutexUnlock _xmlNamespaceParseNCName _xmlNamespaceParseNSDef"
    "_xmlNamespaceParseQName _xmlNanoFTPCheckResponse _xmlNanoFTPCleanup _xmlNanoFTPClose"
    "_xmlNanoFTPCloseConnection _xmlNanoFTPConnect _xmlNanoFTPConnectTo _xmlNanoFTPCwd"
    "_xmlNanoFTPDele _xmlNanoFTPFreeCtxt _xmlNanoFTPGet _xmlNanoFTPGetConnection"
    "_xmlNanoFTPGetResponse _xmlNanoFTPGetSocket _xmlNanoFTPInit _xmlNanoFTPList"
    "_xmlNanoFTPNewCtxt _xmlNanoFTPOpen _xmlNanoFTPProxy _xmlNanoFTPQuit _xmlNanoFTPRead"
    "_xmlNanoFTPScanProxy _xmlNanoFTPUpdateURL _xmlNanoHTTPAuthHeader _xmlNanoHTTPCleanup"
    "_xmlNanoHTTPClose _xmlNanoHTTPContentLength _xmlNanoHTTPEncoding _xmlNanoHTTPFetch"
    "_xmlNanoHTTPInit _xmlNanoHTTPMethod _xmlNanoHTTPMethodRedir _xmlNanoHTTPMimeType"
    "_xmlNanoHTTPOpen _xmlNanoHTTPOpenRedir _xmlNanoHTTPRead _xmlNanoHTTPRedir"
    "_xmlNanoHTTPReturnCode _xmlNanoHTTPSave _xmlNanoHTTPScanProxy _xmlNewAutomata"
    "_xmlNewCDataBlock _xmlNewCatalog _xmlNewCharEncodingHandler _xmlNewCharRef _xmlNewChild"
    "_xmlNewComment _xmlNewDoc _xmlNewDocComment _xmlNewDocElementContent _xmlNewDocFragment"
    "_xmlNewDocNode _xmlNewDocNodeEatName _xmlNewDocPI _xmlNewDocProp _xmlNewDocRawNode"
    "_xmlNewDocText _xmlNewDocTextLen _xmlNewDtd _xmlNewElementContent _xmlNewEntity"
    "_xmlNewEntityInputStream _xmlNewGlobalNs _xmlNewIOInputStream _xmlNewInputFromFile"
    "_xmlNewInputStream _xmlNewMutex _xmlNewNode _xmlNewNodeEatName _xmlNewNs _xmlNewNsProp"
    "_xmlNewNsPropEatName _xmlNewPI _xmlNewParserCtxt _xmlNewProp _xmlNewRMutex"
    "_xmlNewReference _xmlNewStringInputStream _xmlNewText _xmlNewTextChild _xmlNewTextLen"
    "_xmlNewTextReader _xmlNewTextReaderFilename _xmlNewTextWriter _xmlNewTextWriterDoc"
    "_xmlNewTextWriterFilename _xmlNewTextWriterMemory _xmlNewTextWriterPushParser"
    "_xmlNewTextWriterTree _xmlNewValidCtxt _xmlNextChar _xmlNextElementSibling"
    "_xmlNoNetExternalEntityLoader _xmlNodeAddContent _xmlNodeAddContentLen"
    "_xmlNodeBufGetContent _xmlNodeDump _xmlNodeDumpOutput _xmlNodeGetBase _xmlNodeGetContent"
    "_xmlNodeGetLang _xmlNodeGetSpacePreserve _xmlNodeIsText _xmlNodeListGetRawString"
    "_xmlNodeListGetString _xmlNodeSetBase _xmlNodeSetContent _xmlNodeSetContentLen"
    "_xmlNodeSetLang _xmlNodeSetName _xmlNodeSetSpacePreserve _xmlNormalizeURIPath"
    "_xmlNormalizeWindowsPath _xmlOutputBufferClose _xmlOutputBufferCreateBuffer"
    "_xmlOutputBufferCreateFd _xmlOutputBufferCreateFile _xmlOutputBufferCreateFilename"
    "_xmlOutputBufferCreateFilenameDefault _xmlOutputBufferCreateFilenameValue"
    "_xmlOutputBufferCreateIO _xmlOutputBufferFlush _xmlOutputBufferGetContent"
    "_xmlOutputBufferGetSize _xmlOutputBufferWrite _xmlOutputBufferWriteEscape"
    "_xmlOutputBufferWriteString _xmlParseAttValue _xmlParseAttribute"
    "_xmlParseAttributeListDecl _xmlParseAttributeType _xmlParseBalancedChunkMemory"
    "_xmlParseBalancedChunkMemoryRecover _xmlParseCDSect _xmlParseCatalogFile _xmlParseCharData"
    "_xmlParseCharEncoding _xmlParseCharRef _xmlParseChunk _xmlParseComment _xmlParseContent"
    "_xmlParseCtxtExternalEntity _xmlParseDTD _xmlParseDefaultDecl _xmlParseDoc"
    "_xmlParseDocTypeDecl _xmlParseDocument _xmlParseElement"
    "_xmlParseElementChildrenContentDecl _xmlParseElementContentDecl _xmlParseElementDecl"
    "_xmlParseElementMixedContentDecl _xmlParseEncName _xmlParseEncodingDecl _xmlParseEndTag"
    "_xmlParseEntity _xmlParseEntityDecl _xmlParseEntityRef _xmlParseEntityValue"
    "_xmlParseEnumeratedType _xmlParseEnumerationType _xmlParseExtParsedEnt"
    "_xmlParseExternalEntity _xmlParseExternalID _xmlParseExternalSubset _xmlParseFile"
    "_xmlParseInNodeContext _xmlParseMarkupDecl _xmlParseMemory _xmlParseMisc _xmlParseName"
    "_xmlParseNamespace _xmlParseNmtoken _xmlParseNotationDecl _xmlParseNotationType"
    "_xmlParsePEReference _xmlParsePI _xmlParsePITarget _xmlParsePubidLiteral"
    "_xmlParseQuotedString _xmlParseReference _xmlParseSDDecl _xmlParseStartTag"
    "_xmlParseSystemLiteral _xmlParseTextDecl _xmlParseURI _xmlParseURIRaw"
    "_xmlParseURIReference _xmlParseVersionInfo _xmlParseVersionNum _xmlParseXMLDecl"
    "_xmlParserAddNodeInfo _xmlParserDebugEntities _xmlParserError _xmlParserFindNodeInfo"
    "_xmlParserFindNodeInfoIndex _xmlParserGetDirectory _xmlParserHandlePEReference"
    "_xmlParserHandleReference _xmlParserInputBufferCreateFd _xmlParserInputBufferCreateFile"
    "_xmlParserInputBufferCreateFilename _xmlParserInputBufferCreateFilenameDefault"
    "_xmlParserInputBufferCreateFilenameValue _xmlParserInputBufferCreateIO"
    "_xmlParserInputBufferCreateMem _xmlParserInputBufferCreateStatic _xmlParserInputBufferGrow"
    "_xmlParserInputBufferPush _xmlParserInputBufferRead _xmlParserInputGrow"
    "_xmlParserInputRead _xmlParserInputShrink _xmlParserMaxDepth _xmlParserPrintFileContext"
    "_xmlParserPrintFileInfo _xmlParserValidityError _xmlParserValidityWarning"
    "_xmlParserVersion _xmlParserWarning _xmlPathToURI _xmlPatternFromRoot"
    "_xmlPatternGetStreamCtxt _xmlPatternMatch _xmlPatternMaxDepth _xmlPatternMinDepth"
    "_xmlPatternStreamable _xmlPatterncompile _xmlPedanticParserDefault"
    "_xmlPedanticParserDefaultValue _xmlPopInput _xmlPopInputCallbacks _xmlPopOutputCallbacks"
    "_xmlPreviousElementSibling _xmlPrintURI _xmlPushInput _xmlRMutexLock _xmlRMutexUnlock"
    "_xmlReadDoc _xmlReadFd _xmlReadFile _xmlReadIO _xmlReadMemory _xmlReaderForDoc"
    "_xmlReaderForFd _xmlReaderForFile _xmlReaderForIO _xmlReaderForMemory _xmlReaderNewDoc"
    "_xmlReaderNewFd _xmlReaderNewFile _xmlReaderNewIO _xmlReaderNewMemory _xmlReaderNewWalker"
    "_xmlReaderWalker _xmlRealloc _xmlReallocLoc _xmlReconciliateNs _xmlRecoverDoc"
    "_xmlRecoverFile _xmlRecoverMemory _xmlRegExecErrInfo _xmlRegExecNextValues"
    "_xmlRegExecPushString _xmlRegExecPushString2 _xmlRegFreeExecCtxt _xmlRegFreeRegexp"
    "_xmlRegNewExecCtxt _xmlRegexpCompile _xmlRegexpExec _xmlRegexpIsDeterminist"
    "_xmlRegexpPrint _xmlRegisterCharEncodingHandler _xmlRegisterDefaultInputCallbacks"
    "_xmlRegisterDefaultOutputCallbacks _xmlRegisterHTTPPostCallbacks"
    "_xmlRegisterInputCallbacks _xmlRegisterNodeDefault _xmlRegisterNodeDefaultValue"
    "_xmlRegisterOutputCallbacks _xmlRelaxNGCleanupTypes _xmlRelaxNGDump _xmlRelaxNGDumpTree"
    "_xmlRelaxNGFree _xmlRelaxNGFreeParserCtxt _xmlRelaxNGFreeValidCtxt"
    "_xmlRelaxNGGetParserErrors _xmlRelaxNGGetValidErrors _xmlRelaxNGInitTypes"
    "_xmlRelaxNGNewDocParserCtxt _xmlRelaxNGNewMemParserCtxt _xmlRelaxNGNewParserCtxt"
    "_xmlRelaxNGNewValidCtxt _xmlRelaxNGParse _xmlRelaxNGSetParserErrors"
    "_xmlRelaxNGSetParserStructuredErrors _xmlRelaxNGSetValidErrors"
    "_xmlRelaxNGSetValidStructuredErrors _xmlRelaxNGValidateDoc _xmlRelaxNGValidateFullElement"
    "_xmlRelaxNGValidatePopElement _xmlRelaxNGValidatePushCData _xmlRelaxNGValidatePushElement"
    "_xmlRelaxParserSetFlag _xmlRemoveID _xmlRemoveProp _xmlRemoveRef _xmlReplaceNode"
    "_xmlResetError _xmlResetLastError _xmlSAX2AttributeDecl _xmlSAX2CDataBlock"
    "_xmlSAX2Characters _xmlSAX2Comment _xmlSAX2ElementDecl _xmlSAX2EndDocument"
    "_xmlSAX2EndElement _xmlSAX2EndElementNs _xmlSAX2EntityDecl _xmlSAX2ExternalSubset"
    "_xmlSAX2GetColumnNumber _xmlSAX2GetEntity _xmlSAX2GetLineNumber _xmlSAX2GetParameterEntity"
    "_xmlSAX2GetPublicId _xmlSAX2GetSystemId _xmlSAX2HasExternalSubset"
    "_xmlSAX2HasInternalSubset _xmlSAX2IgnorableWhitespace _xmlSAX2InitDefaultSAXHandler"
    "_xmlSAX2InitDocbDefaultSAXHandler _xmlSAX2InitHtmlDefaultSAXHandler _xmlSAX2InternalSubset"
    "_xmlSAX2IsStandalone _xmlSAX2NotationDecl _xmlSAX2ProcessingInstruction _xmlSAX2Reference"
    "_xmlSAX2ResolveEntity _xmlSAX2SetDocumentLocator _xmlSAX2StartDocument"
    "_xmlSAX2StartElement _xmlSAX2StartElementNs _xmlSAX2UnparsedEntityDecl"
    "_xmlSAXDefaultVersion _xmlSAXParseDTD _xmlSAXParseDoc _xmlSAXParseEntity _xmlSAXParseFile"
    "_xmlSAXParseFileWithData _xmlSAXParseMemory _xmlSAXParseMemoryWithData"
    "_xmlSAXUserParseFile _xmlSAXUserParseMemory _xmlSAXVersion _xmlSaveClose _xmlSaveDoc"
    "_xmlSaveFile _xmlSaveFileEnc _xmlSaveFileTo _xmlSaveFlush _xmlSaveFormatFile"
    "_xmlSaveFormatFileEnc _xmlSaveFormatFileTo _xmlSaveNoEmptyTags _xmlSaveSetAttrEscape"
    "_xmlSaveSetEscape _xmlSaveToBuffer _xmlSaveToFd _xmlSaveToFilename _xmlSaveToIO"
    "_xmlSaveTree _xmlSaveUri _xmlScanName _xmlSchemaCheckFacet _xmlSchemaCleanupTypes"
    "_xmlSchemaCollapseString _xmlSchemaCompareValues _xmlSchemaCompareValuesWhtsp"
    "_xmlSchemaCopyValue _xmlSchemaDump _xmlSchemaFree _xmlSchemaFreeFacet"
    "_xmlSchemaFreeParserCtxt _xmlSchemaFreeType _xmlSchemaFreeValidCtxt _xmlSchemaFreeValue"
    "_xmlSchemaFreeWildcard _xmlSchemaGetBuiltInListSimpleTypeItemType _xmlSchemaGetBuiltInType"
    "_xmlSchemaGetCanonValue _xmlSchemaGetCanonValueWhtsp _xmlSchemaGetFacetValueAsULong"
    "_xmlSchemaGetParserErrors _xmlSchemaGetPredefinedType _xmlSchemaGetValType"
    "_xmlSchemaGetValidErrors _xmlSchemaInitTypes _xmlSchemaIsBuiltInTypeFacet"
    "_xmlSchemaIsValid _xmlSchemaNewDocParserCtxt _xmlSchemaNewFacet _xmlSchemaNewMemParserCtxt"
    "_xmlSchemaNewNOTATIONValue _xmlSchemaNewParserCtxt _xmlSchemaNewQNameValue"
    "_xmlSchemaNewStringValue _xmlSchemaNewValidCtxt _xmlSchemaParse _xmlSchemaSAXPlug"
    "_xmlSchemaSAXUnplug _xmlSchemaSetParserErrors _xmlSchemaSetParserStructuredErrors"
    "_xmlSchemaSetValidErrors _xmlSchemaSetValidOptions _xmlSchemaSetValidStructuredErrors"
    "_xmlSchemaValPredefTypeNode _xmlSchemaValPredefTypeNodeNoNorm"
    "_xmlSchemaValidCtxtGetOptions _xmlSchemaValidCtxtGetParserCtxt _xmlSchemaValidateDoc"
    "_xmlSchemaValidateFacet _xmlSchemaValidateFacetWhtsp _xmlSchemaValidateFile"
    "_xmlSchemaValidateLengthFacet _xmlSchemaValidateLengthFacetWhtsp"
    "_xmlSchemaValidateListSimpleTypeFacet _xmlSchemaValidateOneElement"
    "_xmlSchemaValidatePredefinedType _xmlSchemaValidateSetFilename"
    "_xmlSchemaValidateSetLocator _xmlSchemaValidateStream _xmlSchemaValueAppend"
    "_xmlSchemaValueGetAsBoolean _xmlSchemaValueGetAsString _xmlSchemaValueGetNext"
    "_xmlSchemaWhiteSpaceReplace _xmlSchematronFree _xmlSchematronFreeParserCtxt"
    "_xmlSchematronFreeValidCtxt _xmlSchematronNewDocParserCtxt _xmlSchematronNewMemParserCtxt"
    "_xmlSchematronNewParserCtxt _xmlSchematronNewValidCtxt _xmlSchematronParse"
    "_xmlSchematronSetValidStructuredErrors _xmlSchematronValidateDoc _xmlSearchNs"
    "_xmlSearchNsByHref _xmlSetBufferAllocationScheme _xmlSetCompressMode"
    "_xmlSetDocCompressMode _xmlSetEntityReferenceFunc _xmlSetExternalEntityLoader"
    "_xmlSetFeature _xmlSetGenericErrorFunc _xmlSetListDoc _xmlSetNs _xmlSetNsProp _xmlSetProp"
    "_xmlSetStructuredErrorFunc _xmlSetTreeDoc _xmlSetupParserForBuffer _xmlShell _xmlShellBase"
    "_xmlShellCat _xmlShellDir _xmlShellDu _xmlShellList _xmlShellLoad _xmlShellPrintNode"
    "_xmlShellPrintXPathError _xmlShellPrintXPathResult _xmlShellPwd _xmlShellSave"
    "_xmlShellValidate _xmlShellWrite _xmlSkipBlankChars _xmlSnprintfElementContent"
    "_xmlSplitQName _xmlSplitQName2 _xmlSplitQName3 _xmlSprintfElementContent _xmlStopParser"
    "_xmlStrEqual _xmlStrPrintf _xmlStrQEqual _xmlStrVPrintf _xmlStrcasecmp _xmlStrcasestr"
    "_xmlStrcat _xmlStrchr _xmlStrcmp _xmlStrdup _xmlStreamPop _xmlStreamPush"
    "_xmlStreamPushAttr _xmlStreamPushNode _xmlStreamWantsAnyNode _xmlStringComment"
    "_xmlStringCurrentChar _xmlStringDecodeEntities _xmlStringGetNodeList"
    "_xmlStringLenDecodeEntities _xmlStringLenGetNodeList _xmlStringText _xmlStringTextNoenc"
    "_xmlStrlen _xmlStrncasecmp _xmlStrncat _xmlStrncatNew _xmlStrncmp _xmlStrndup _xmlStrstr"
    "_xmlStrsub _xmlStructuredError _xmlStructuredErrorContext _xmlSubstituteEntitiesDefault"
    "_xmlSubstituteEntitiesDefaultValue _xmlSwitchEncoding _xmlSwitchInputEncoding"
    "_xmlSwitchToEncoding _xmlTextConcat _xmlTextMerge _xmlTextReaderAttributeCount"
    "_xmlTextReaderBaseUri _xmlTextReaderByteConsumed _xmlTextReaderClose"
    "_xmlTextReaderConstBaseUri _xmlTextReaderConstEncoding _xmlTextReaderConstLocalName"
    "_xmlTextReaderConstName _xmlTextReaderConstNamespaceUri _xmlTextReaderConstPrefix"
    "_xmlTextReaderConstString _xmlTextReaderConstValue _xmlTextReaderConstXmlLang"
    "_xmlTextReaderConstXmlVersion _xmlTextReaderCurrentDoc _xmlTextReaderCurrentNode"
    "_xmlTextReaderDepth _xmlTextReaderExpand _xmlTextReaderGetAttribute"
    "_xmlTextReaderGetAttributeNo _xmlTextReaderGetAttributeNs _xmlTextReaderGetErrorHandler"
    "_xmlTextReaderGetParserColumnNumber _xmlTextReaderGetParserLineNumber"
    "_xmlTextReaderGetParserProp _xmlTextReaderGetRemainder _xmlTextReaderHasAttributes"
    "_xmlTextReaderHasValue _xmlTextReaderIsDefault _xmlTextReaderIsEmptyElement"
    "_xmlTextReaderIsNamespaceDecl _xmlTextReaderIsValid _xmlTextReaderLocalName"
    "_xmlTextReaderLocatorBaseURI _xmlTextReaderLocatorLineNumber _xmlTextReaderLookupNamespace"
    "_xmlTextReaderMoveToAttribute _xmlTextReaderMoveToAttributeNo"
    "_xmlTextReaderMoveToAttributeNs _xmlTextReaderMoveToElement"
    "_xmlTextReaderMoveToFirstAttribute _xmlTextReaderMoveToNextAttribute _xmlTextReaderName"
    "_xmlTextReaderNamespaceUri _xmlTextReaderNext _xmlTextReaderNextSibling"
    "_xmlTextReaderNodeType _xmlTextReaderNormalization _xmlTextReaderPrefix"
    "_xmlTextReaderPreserve _xmlTextReaderPreservePattern _xmlTextReaderQuoteChar"
    "_xmlTextReaderRead _xmlTextReaderReadAttributeValue _xmlTextReaderReadInnerXml"
    "_xmlTextReaderReadOuterXml _xmlTextReaderReadState _xmlTextReaderReadString"
    "_xmlTextReaderRelaxNGSetSchema _xmlTextReaderRelaxNGValidate"
    "_xmlTextReaderRelaxNGValidateCtxt _xmlTextReaderSchemaValidate"
    "_xmlTextReaderSchemaValidateCtxt _xmlTextReaderSetErrorHandler _xmlTextReaderSetParserProp"
    "_xmlTextReaderSetSchema _xmlTextReaderSetStructuredErrorHandler _xmlTextReaderSetup"
    "_xmlTextReaderStandalone _xmlTextReaderValue _xmlTextReaderXmlLang"
    "_xmlTextWriterEndAttribute _xmlTextWriterEndCDATA _xmlTextWriterEndComment"
    "_xmlTextWriterEndDTD _xmlTextWriterEndDTDAttlist _xmlTextWriterEndDTDElement"
    "_xmlTextWriterEndDTDEntity _xmlTextWriterEndDocument _xmlTextWriterEndElement"
    "_xmlTextWriterEndPI _xmlTextWriterFlush _xmlTextWriterFullEndElement"
    "_xmlTextWriterSetIndent _xmlTextWriterSetIndentString _xmlTextWriterSetQuoteChar"
    "_xmlTextWriterStartAttribute _xmlTextWriterStartAttributeNS _xmlTextWriterStartCDATA"
    "_xmlTextWriterStartComment _xmlTextWriterStartDTD _xmlTextWriterStartDTDAttlist"
    "_xmlTextWriterStartDTDElement _xmlTextWriterStartDTDEntity _xmlTextWriterStartDocument"
    "_xmlTextWriterStartElement _xmlTextWriterStartElementNS _xmlTextWriterStartPI"
    "_xmlTextWriterWriteAttribute _xmlTextWriterWriteAttributeNS _xmlTextWriterWriteBase64"
    "_xmlTextWriterWriteBinHex _xmlTextWriterWriteCDATA _xmlTextWriterWriteComment"
    "_xmlTextWriterWriteDTD _xmlTextWriterWriteDTDAttlist _xmlTextWriterWriteDTDElement"
    "_xmlTextWriterWriteDTDEntity _xmlTextWriterWriteDTDExternalEntity"
    "_xmlTextWriterWriteDTDExternalEntityContents _xmlTextWriterWriteDTDInternalEntity"
    "_xmlTextWriterWriteDTDNotation _xmlTextWriterWriteElement _xmlTextWriterWriteElementNS"
    "_xmlTextWriterWriteFormatAttribute _xmlTextWriterWriteFormatAttributeNS"
    "_xmlTextWriterWriteFormatCDATA _xmlTextWriterWriteFormatComment"
    "_xmlTextWriterWriteFormatDTD _xmlTextWriterWriteFormatDTDAttlist"
    "_xmlTextWriterWriteFormatDTDElement _xmlTextWriterWriteFormatDTDInternalEntity"
    "_xmlTextWriterWriteFormatElement _xmlTextWriterWriteFormatElementNS"
    "_xmlTextWriterWriteFormatPI _xmlTextWriterWriteFormatRaw _xmlTextWriterWriteFormatString"
    "_xmlTextWriterWritePI _xmlTextWriterWriteRaw _xmlTextWriterWriteRawLen"
    "_xmlTextWriterWriteString _xmlTextWriterWriteVFormatAttribute"
    "_xmlTextWriterWriteVFormatAttributeNS _xmlTextWriterWriteVFormatCDATA"
    "_xmlTextWriterWriteVFormatComment _xmlTextWriterWriteVFormatDTD"
    "_xmlTextWriterWriteVFormatDTDAttlist _xmlTextWriterWriteVFormatDTDElement"
    "_xmlTextWriterWriteVFormatDTDInternalEntity _xmlTextWriterWriteVFormatElement"
    "_xmlTextWriterWriteVFormatElementNS _xmlTextWriterWriteVFormatPI"
    "_xmlTextWriterWriteVFormatRaw _xmlTextWriterWriteVFormatString _xmlThrDefBufferAllocScheme"
    "_xmlThrDefDefaultBufferSize _xmlThrDefDeregisterNodeDefault"
    "_xmlThrDefDoValidityCheckingDefaultValue _xmlThrDefGetWarningsDefaultValue"
    "_xmlThrDefIndentTreeOutput _xmlThrDefKeepBlanksDefaultValue"
    "_xmlThrDefLineNumbersDefaultValue _xmlThrDefLoadExtDtdDefaultValue"
    "_xmlThrDefOutputBufferCreateFilenameDefault _xmlThrDefParserDebugEntities"
    "_xmlThrDefParserInputBufferCreateFilenameDefault _xmlThrDefPedanticParserDefaultValue"
    "_xmlThrDefRegisterNodeDefault _xmlThrDefSaveNoEmptyTags _xmlThrDefSetGenericErrorFunc"
    "_xmlThrDefSetStructuredErrorFunc _xmlThrDefSubstituteEntitiesDefaultValue"
    "_xmlThrDefTreeIndentString _xmlTreeIndentString _xmlUCSIsAegeanNumbers"
    "_xmlUCSIsAlphabeticPresentationForms _xmlUCSIsArabic _xmlUCSIsArabicPresentationFormsA"
    "_xmlUCSIsArabicPresentationFormsB _xmlUCSIsArmenian _xmlUCSIsArrows _xmlUCSIsBasicLatin"
    "_xmlUCSIsBengali _xmlUCSIsBlock _xmlUCSIsBlockElements _xmlUCSIsBopomofo"
    "_xmlUCSIsBopomofoExtended _xmlUCSIsBoxDrawing _xmlUCSIsBraillePatterns _xmlUCSIsBuhid"
    "_xmlUCSIsByzantineMusicalSymbols _xmlUCSIsCJKCompatibility _xmlUCSIsCJKCompatibilityForms"
    "_xmlUCSIsCJKCompatibilityIdeographs _xmlUCSIsCJKCompatibilityIdeographsSupplement"
    "_xmlUCSIsCJKRadicalsSupplement _xmlUCSIsCJKSymbolsandPunctuation"
    "_xmlUCSIsCJKUnifiedIdeographs _xmlUCSIsCJKUnifiedIdeographsExtensionA"
    "_xmlUCSIsCJKUnifiedIdeographsExtensionB _xmlUCSIsCat _xmlUCSIsCatC _xmlUCSIsCatCc"
    "_xmlUCSIsCatCf _xmlUCSIsCatCo _xmlUCSIsCatCs _xmlUCSIsCatL _xmlUCSIsCatLl _xmlUCSIsCatLm"
    "_xmlUCSIsCatLo _xmlUCSIsCatLt _xmlUCSIsCatLu _xmlUCSIsCatM _xmlUCSIsCatMc _xmlUCSIsCatMe"
    "_xmlUCSIsCatMn _xmlUCSIsCatN _xmlUCSIsCatNd _xmlUCSIsCatNl _xmlUCSIsCatNo _xmlUCSIsCatP"
    "_xmlUCSIsCatPc _xmlUCSIsCatPd _xmlUCSIsCatPe _xmlUCSIsCatPf _xmlUCSIsCatPi _xmlUCSIsCatPo"
    "_xmlUCSIsCatPs _xmlUCSIsCatS _xmlUCSIsCatSc _xmlUCSIsCatSk _xmlUCSIsCatSm _xmlUCSIsCatSo"
    "_xmlUCSIsCatZ _xmlUCSIsCatZl _xmlUCSIsCatZp _xmlUCSIsCatZs _xmlUCSIsCherokee"
    "_xmlUCSIsCombiningDiacriticalMarks _xmlUCSIsCombiningDiacriticalMarksforSymbols"
    "_xmlUCSIsCombiningHalfMarks _xmlUCSIsCombiningMarksforSymbols _xmlUCSIsControlPictures"
    "_xmlUCSIsCurrencySymbols _xmlUCSIsCypriotSyllabary _xmlUCSIsCyrillic"
    "_xmlUCSIsCyrillicSupplement _xmlUCSIsDeseret _xmlUCSIsDevanagari _xmlUCSIsDingbats"
    "_xmlUCSIsEnclosedAlphanumerics _xmlUCSIsEnclosedCJKLettersandMonths _xmlUCSIsEthiopic"
    "_xmlUCSIsGeneralPunctuation _xmlUCSIsGeometricShapes _xmlUCSIsGeorgian _xmlUCSIsGothic"
    "_xmlUCSIsGreek _xmlUCSIsGreekExtended _xmlUCSIsGreekandCoptic _xmlUCSIsGujarati"
    "_xmlUCSIsGurmukhi _xmlUCSIsHalfwidthandFullwidthForms _xmlUCSIsHangulCompatibilityJamo"
    "_xmlUCSIsHangulJamo _xmlUCSIsHangulSyllables _xmlUCSIsHanunoo _xmlUCSIsHebrew"
    "_xmlUCSIsHighPrivateUseSurrogates _xmlUCSIsHighSurrogates _xmlUCSIsHiragana"
    "_xmlUCSIsIPAExtensions _xmlUCSIsIdeographicDescriptionCharacters _xmlUCSIsKanbun"
    "_xmlUCSIsKangxiRadicals _xmlUCSIsKannada _xmlUCSIsKatakana"
    "_xmlUCSIsKatakanaPhoneticExtensions _xmlUCSIsKhmer _xmlUCSIsKhmerSymbols _xmlUCSIsLao"
    "_xmlUCSIsLatin1Supplement _xmlUCSIsLatinExtendedA _xmlUCSIsLatinExtendedAdditional"
    "_xmlUCSIsLatinExtendedB _xmlUCSIsLetterlikeSymbols _xmlUCSIsLimbu"
    "_xmlUCSIsLinearBIdeograms _xmlUCSIsLinearBSyllabary _xmlUCSIsLowSurrogates"
    "_xmlUCSIsMalayalam _xmlUCSIsMathematicalAlphanumericSymbols _xmlUCSIsMathematicalOperators"
    "_xmlUCSIsMiscellaneousMathematicalSymbolsA _xmlUCSIsMiscellaneousMathematicalSymbolsB"
    "_xmlUCSIsMiscellaneousSymbols _xmlUCSIsMiscellaneousSymbolsandArrows"
    "_xmlUCSIsMiscellaneousTechnical _xmlUCSIsMongolian _xmlUCSIsMusicalSymbols"
    "_xmlUCSIsMyanmar _xmlUCSIsNumberForms _xmlUCSIsOgham _xmlUCSIsOldItalic"
    "_xmlUCSIsOpticalCharacterRecognition _xmlUCSIsOriya _xmlUCSIsOsmanya"
    "_xmlUCSIsPhoneticExtensions _xmlUCSIsPrivateUse _xmlUCSIsPrivateUseArea _xmlUCSIsRunic"
    "_xmlUCSIsShavian _xmlUCSIsSinhala _xmlUCSIsSmallFormVariants"
    "_xmlUCSIsSpacingModifierLetters _xmlUCSIsSpecials _xmlUCSIsSuperscriptsandSubscripts"
    "_xmlUCSIsSupplementalArrowsA _xmlUCSIsSupplementalArrowsB"
    "_xmlUCSIsSupplementalMathematicalOperators _xmlUCSIsSupplementaryPrivateUseAreaA"
    "_xmlUCSIsSupplementaryPrivateUseAreaB _xmlUCSIsSyriac _xmlUCSIsTagalog _xmlUCSIsTagbanwa"
    "_xmlUCSIsTags _xmlUCSIsTaiLe _xmlUCSIsTaiXuanJingSymbols _xmlUCSIsTamil _xmlUCSIsTelugu"
    "_xmlUCSIsThaana _xmlUCSIsThai _xmlUCSIsTibetan _xmlUCSIsUgaritic"
    "_xmlUCSIsUnifiedCanadianAboriginalSyllabics _xmlUCSIsVariationSelectors"
    "_xmlUCSIsVariationSelectorsSupplement _xmlUCSIsYiRadicals _xmlUCSIsYiSyllables"
    "_xmlUCSIsYijingHexagramSymbols _xmlURIEscape _xmlURIEscapeStr _xmlURIUnescapeString"
    "_xmlUTF8Charcmp _xmlUTF8Size _xmlUTF8Strlen _xmlUTF8Strloc _xmlUTF8Strndup _xmlUTF8Strpos"
    "_xmlUTF8Strsize _xmlUTF8Strsub _xmlUnlinkNode _xmlUnlockLibrary _xmlUnsetNsProp"
    "_xmlUnsetProp _xmlValidBuildContentModel _xmlValidCtxtNormalizeAttributeValue"
    "_xmlValidGetPotentialChildren _xmlValidGetValidElements _xmlValidNormalizeAttributeValue"
    "_xmlValidateAttributeDecl _xmlValidateAttributeValue _xmlValidateDocument"
    "_xmlValidateDocumentFinal _xmlValidateDtd _xmlValidateDtdFinal _xmlValidateElement"
    "_xmlValidateElementDecl _xmlValidateNCName _xmlValidateNMToken _xmlValidateName"
    "_xmlValidateNameValue _xmlValidateNamesValue _xmlValidateNmtokenValue"
    "_xmlValidateNmtokensValue _xmlValidateNotationDecl _xmlValidateNotationUse"
    "_xmlValidateOneAttribute _xmlValidateOneElement _xmlValidateOneNamespace"
    "_xmlValidatePopElement _xmlValidatePushCData _xmlValidatePushElement _xmlValidateQName"
    "_xmlValidateRoot _xmlXIncludeFreeContext _xmlXIncludeNewContext _xmlXIncludeProcess"
    "_xmlXIncludeProcessFlags _xmlXIncludeProcessFlagsData _xmlXIncludeProcessNode"
    "_xmlXIncludeProcessTree _xmlXIncludeProcessTreeFlags _xmlXIncludeProcessTreeFlagsData"
    "_xmlXIncludeSetFlags _xmlXPathAddValues _xmlXPathBooleanFunction"
    "_xmlXPathCastBooleanToNumber _xmlXPathCastBooleanToString _xmlXPathCastNodeSetToBoolean"
    "_xmlXPathCastNodeSetToNumber _xmlXPathCastNodeSetToString _xmlXPathCastNodeToNumber"
    "_xmlXPathCastNodeToString _xmlXPathCastNumberToBoolean _xmlXPathCastNumberToString"
    "_xmlXPathCastStringToBoolean _xmlXPathCastStringToNumber _xmlXPathCastToBoolean"
    "_xmlXPathCastToNumber _xmlXPathCastToString _xmlXPathCeilingFunction _xmlXPathCmpNodes"
    "_xmlXPathCompareValues _xmlXPathCompile _xmlXPathCompiledEval"
    "_xmlXPathCompiledEvalToBoolean _xmlXPathConcatFunction _xmlXPathContainsFunction"
    "_xmlXPathContextSetCache _xmlXPathConvertBoolean _xmlXPathConvertNumber"
    "_xmlXPathConvertString _xmlXPathCountFunction _xmlXPathCtxtCompile"
    "_xmlXPathDebugDumpCompExpr _xmlXPathDebugDumpObject _xmlXPathDifference _xmlXPathDistinct"
    "_xmlXPathDistinctSorted _xmlXPathDivValues _xmlXPathEqualValues _xmlXPathErr _xmlXPathEval"
    "_xmlXPathEvalExpr _xmlXPathEvalExpression _xmlXPathEvalPredicate"
    "_xmlXPathEvaluatePredicateResult _xmlXPathFalseFunction _xmlXPathFloorFunction"
    "_xmlXPathFreeCompExpr _xmlXPathFreeContext _xmlXPathFreeNodeSet _xmlXPathFreeNodeSetList"
    "_xmlXPathFreeObject _xmlXPathFreeParserContext _xmlXPathFunctionLookup"
    "_xmlXPathFunctionLookupNS _xmlXPathHasSameNodes _xmlXPathIdFunction _xmlXPathInit"
    "_xmlXPathIntersection _xmlXPathIsInf _xmlXPathIsNaN _xmlXPathIsNodeType"
    "_xmlXPathLangFunction _xmlXPathLastFunction _xmlXPathLeading _xmlXPathLeadingSorted"
    "_xmlXPathLocalNameFunction _xmlXPathModValues _xmlXPathMultValues _xmlXPathNAN"
    "_xmlXPathNINF _xmlXPathNamespaceURIFunction _xmlXPathNewBoolean _xmlXPathNewCString"
    "_xmlXPathNewContext _xmlXPathNewFloat _xmlXPathNewNodeSet _xmlXPathNewNodeSetList"
    "_xmlXPathNewParserContext _xmlXPathNewString _xmlXPathNewValueTree _xmlXPathNextAncestor"
    "_xmlXPathNextAncestorOrSelf _xmlXPathNextAttribute _xmlXPathNextChild"
    "_xmlXPathNextDescendant _xmlXPathNextDescendantOrSelf _xmlXPathNextFollowing"
    "_xmlXPathNextFollowingSibling _xmlXPathNextNamespace _xmlXPathNextParent"
    "_xmlXPathNextPreceding _xmlXPathNextPrecedingSibling _xmlXPathNextSelf _xmlXPathNodeEval"
    "_xmlXPathNodeLeading _xmlXPathNodeLeadingSorted _xmlXPathNodeSetAdd _xmlXPathNodeSetAddNs"
    "_xmlXPathNodeSetAddUnique _xmlXPathNodeSetContains _xmlXPathNodeSetCreate"
    "_xmlXPathNodeSetDel _xmlXPathNodeSetFreeNs _xmlXPathNodeSetMerge _xmlXPathNodeSetRemove"
    "_xmlXPathNodeSetSort _xmlXPathNodeTrailing _xmlXPathNodeTrailingSorted"
    "_xmlXPathNormalizeFunction _xmlXPathNotEqualValues _xmlXPathNotFunction _xmlXPathNsLookup"
    "_xmlXPathNumberFunction _xmlXPathObjectCopy _xmlXPathOrderDocElems _xmlXPathPINF"
    "_xmlXPathParseNCName _xmlXPathParseName _xmlXPathPopBoolean _xmlXPathPopExternal"
    "_xmlXPathPopNodeSet _xmlXPathPopNumber _xmlXPathPopString _xmlXPathPositionFunction"
    "_xmlXPathRegisterAllFunctions _xmlXPathRegisterFunc _xmlXPathRegisterFuncLookup"
    "_xmlXPathRegisterFuncNS _xmlXPathRegisterNs _xmlXPathRegisterVariable"
    "_xmlXPathRegisterVariableLookup _xmlXPathRegisterVariableNS"
    "_xmlXPathRegisteredFuncsCleanup _xmlXPathRegisteredNsCleanup"
    "_xmlXPathRegisteredVariablesCleanup _xmlXPathRoot _xmlXPathRoundFunction"
    "_xmlXPathSetContextNode _xmlXPathStartsWithFunction _xmlXPathStringEvalNumber"
    "_xmlXPathStringFunction _xmlXPathStringLengthFunction _xmlXPathSubValues"
    "_xmlXPathSubstringAfterFunction _xmlXPathSubstringBeforeFunction"
    "_xmlXPathSubstringFunction _xmlXPathSumFunction _xmlXPathTrailing _xmlXPathTrailingSorted"
    "_xmlXPathTranslateFunction _xmlXPathTrueFunction _xmlXPathValueFlipSign"
    "_xmlXPathVariableLookup _xmlXPathVariableLookupNS _xmlXPathWrapCString"
    "_xmlXPathWrapExternal _xmlXPathWrapNodeSet _xmlXPathWrapString _xmlXPatherror"
    "_xmlXPtrBuildNodeList _xmlXPtrEval _xmlXPtrEvalRangePredicate _xmlXPtrFreeLocationSet"
    "_xmlXPtrLocationSetAdd _xmlXPtrLocationSetCreate _xmlXPtrLocationSetDel"
    "_xmlXPtrLocationSetMerge _xmlXPtrLocationSetRemove _xmlXPtrNewCollapsedRange"
    "_xmlXPtrNewContext _xmlXPtrNewLocationSetNodeSet _xmlXPtrNewLocationSetNodes"
    "_xmlXPtrNewRange _xmlXPtrNewRangeNodeObject _xmlXPtrNewRangeNodePoint"
    "_xmlXPtrNewRangeNodes _xmlXPtrNewRangePointNode _xmlXPtrNewRangePoints"
    "_xmlXPtrRangeToFunction _xmlXPtrWrapLocationSet"
).split()

_LIBICONV_2_SYMS = (
    "___bsd___iconv ___bsd___iconv_free_list ___bsd___iconv_get_list ___bsd_iconv"
    "___bsd_iconv_canonicalize ___bsd_iconv_close ___bsd_iconv_open ___bsd_iconv_open_into"
    "___bsd_iconv_set_relocation_prefix ___bsd_iconvctl ___bsd_iconvlist ___iconv"
    "___iconv_free_list ___iconv_get_list __citrus_NONE_stdenc_ops __citrus_NONE_stdenc_traits"
    "__citrus_bcs_convert_to_lower __citrus_bcs_convert_to_upper __citrus_bcs_skip_nonws"
    "__citrus_bcs_skip_nonws_len __citrus_bcs_skip_ws __citrus_bcs_skip_ws_len"
    "__citrus_bcs_strcasecmp __citrus_bcs_strncasecmp __citrus_bcs_strtol __citrus_bcs_strtoul"
    "__citrus_bcs_trunc_rws_len __citrus_csmapper_open __citrus_db_close"
    "__citrus_db_factory_add __citrus_db_factory_add16_by_string"
    "__citrus_db_factory_add32_by_string __citrus_db_factory_add8_by_string"
    "__citrus_db_factory_add_by_string __citrus_db_factory_add_string_by_string"
    "__citrus_db_factory_calc_size __citrus_db_factory_create __citrus_db_factory_free"
    "__citrus_db_factory_serialize __citrus_db_get_entry __citrus_db_get_number_of_entries"
    "__citrus_db_hash_std __citrus_db_lookup __citrus_db_lookup16_by_string"
    "__citrus_db_lookup32_by_string __citrus_db_lookup8_by_string __citrus_db_lookup_by_string"
    "__citrus_db_lookup_string_by_string __citrus_db_open __citrus_esdb_alias"
    "__citrus_esdb_close __citrus_esdb_free_list __citrus_esdb_get_list __citrus_esdb_open"
    "__citrus_find_getops __citrus_iconv_canonicalize __citrus_iconv_close __citrus_iconv_open"
    "__citrus_load_module __citrus_lookup_factory_convert __citrus_lookup_get_number_of_entries"
    "__citrus_lookup_seq_close __citrus_lookup_seq_lookup __citrus_lookup_seq_next"
    "__citrus_lookup_seq_open __citrus_lookup_seq_rewind __citrus_lookup_simple"
    "__citrus_map_file __citrus_mapper_close __citrus_mapper_create_area"
    "__citrus_mapper_get_mapdir_from_key __citrus_mapper_open __citrus_mapper_open_direct"
    "__citrus_mapper_set_persistent __citrus_memory_stream_chr __citrus_memory_stream_getln"
    "__citrus_memory_stream_matchline __citrus_memory_stream_skip_ws"
    "__citrus_pivot_factory_convert __citrus_prop_parse_variable __citrus_stdenc_close"
    "__citrus_stdenc_default __citrus_stdenc_open __citrus_unload_module __citrus_unmap_file"
    "__libiconv_version __string_hash_func _iconv _iconv_canonicalize _iconv_close _iconv_open"
    "_iconv_open_into _iconvctl _iconvlist _libiconv_set_relocation_prefix"
).split()

_LIBCOMPRESSION_SYMS = (
    "_compression_decode_buffer _compression_decode_scratch_buffer_size"
    "_compression_encode_buffer _compression_encode_scratch_buffer_size"
    "_compression_stream_destroy _compression_stream_get_decode_state_size"
    "_compression_stream_get_encode_state_size _compression_stream_get_state_size"
    "_compression_stream_identify_algorithm _compression_stream_init"
    "_compression_stream_init_with_state_buffer _compression_stream_is_state_valid"
    "_compression_stream_process _compression_stream_reinit _cosl_codec_decode"
    "_cosl_codec_encode _cosl_codec_get_decoded_size _cosl_codec_get_id _cosl_codec_map"
    "_cosl_codec_unmap _cosl_model_create _cosl_model_destroy _cosl_model_save_codec"
    "_cosl_model_update _cosmix_codec_decode _cosmix_codec_encode"
    "_cosmix_codec_get_decoded_size _cosmix_codec_get_id _cosmix_codec_map _cosmix_codec_unmap"
    "_cosmix_model_create _cosmix_model_destroy _cosmix_model_save_codec _cosmix_model_update"
    "_touchpadCodecCreate _touchpadCodecDecodeImage _touchpadCodecDestroy"
    "_touchpadCodecEncodeImage _touchpadGetInfoWithCompressedBuffer _yzip_codec_create"
    "_yzip_codec_destroy _yzip_image_create _yzip_image_create_with_payload _yzip_image_decode"
    "_yzip_image_destroy _yzip_image_encode _yzip_image_get_descriptor"
    "_yzip_image_get_max_payload_size _yzip_image_get_plane_descriptor _yzip_image_set_data"
    "_yzip_image_set_identifier _yzip_image_set_plane_data _zero_coder_decode"
    "_zero_coder_encode"
).split()

_LIBBZ2_1_0_SYMS = (
    "_BZ2_bzBuffToBuffCompress _BZ2_bzBuffToBuffDecompress _BZ2_bzCompress _BZ2_bzCompressEnd"
    "_BZ2_bzCompressInit _BZ2_bzDecompress _BZ2_bzDecompressEnd _BZ2_bzDecompressInit"
    "_BZ2_bzRead _BZ2_bzReadClose _BZ2_bzReadGetUnused _BZ2_bzReadOpen _BZ2_bzWrite"
    "_BZ2_bzWriteClose _BZ2_bzWriteClose64 _BZ2_bzWriteOpen _BZ2_bzclose _BZ2_bzdopen"
    "_BZ2_bzerror _BZ2_bzflush _BZ2_bzlibVersion _BZ2_bzopen _BZ2_bzread _BZ2_bzwrite"
).split()

_LIBLZMA_5_SYMS = (
    "_lzma_alone_decoder _lzma_alone_encoder _lzma_auto_decoder _lzma_block_buffer_bound"
    "_lzma_block_buffer_decode _lzma_block_buffer_encode _lzma_block_compressed_size"
    "_lzma_block_decoder _lzma_block_encoder _lzma_block_header_decode"
    "_lzma_block_header_encode _lzma_block_header_size _lzma_block_total_size"
    "_lzma_block_uncomp_encode _lzma_block_unpadded_size _lzma_check_is_supported"
    "_lzma_check_size _lzma_code _lzma_cputhreads _lzma_crc32 _lzma_crc64"
    "_lzma_easy_buffer_encode _lzma_easy_decoder_memusage _lzma_easy_encoder"
    "_lzma_easy_encoder_memusage _lzma_end _lzma_file_info_decoder"
    "_lzma_filter_decoder_is_supported _lzma_filter_encoder_is_supported"
    "_lzma_filter_flags_decode _lzma_filter_flags_encode _lzma_filter_flags_size"
    "_lzma_filters_copy _lzma_filters_free _lzma_filters_update _lzma_get_check"
    "_lzma_get_progress _lzma_index_append _lzma_index_block_count _lzma_index_buffer_decode"
    "_lzma_index_buffer_encode _lzma_index_cat _lzma_index_checks _lzma_index_decoder"
    "_lzma_index_dup _lzma_index_encoder _lzma_index_end _lzma_index_file_size"
    "_lzma_index_hash_append _lzma_index_hash_decode _lzma_index_hash_end _lzma_index_hash_init"
    "_lzma_index_hash_size _lzma_index_init _lzma_index_iter_init _lzma_index_iter_locate"
    "_lzma_index_iter_next _lzma_index_iter_rewind _lzma_index_memusage _lzma_index_memused"
    "_lzma_index_size _lzma_index_stream_count _lzma_index_stream_flags"
    "_lzma_index_stream_padding _lzma_index_stream_size _lzma_index_total_size"
    "_lzma_index_uncompressed_size _lzma_lzip_decoder _lzma_lzma_preset _lzma_memlimit_get"
    "_lzma_memlimit_set _lzma_memusage _lzma_mf_is_supported _lzma_microlzma_decoder"
    "_lzma_microlzma_encoder _lzma_mode_is_supported _lzma_physmem _lzma_properties_decode"
    "_lzma_properties_encode _lzma_properties_size _lzma_raw_buffer_decode"
    "_lzma_raw_buffer_encode _lzma_raw_decoder _lzma_raw_decoder_memusage _lzma_raw_encoder"
    "_lzma_raw_encoder_memusage _lzma_str_from_filters _lzma_str_list_filters"
    "_lzma_str_to_filters _lzma_stream_buffer_bound _lzma_stream_buffer_decode"
    "_lzma_stream_buffer_encode _lzma_stream_decoder _lzma_stream_decoder_mt"
    "_lzma_stream_encoder _lzma_stream_encoder_mt _lzma_stream_encoder_mt_memusage"
    "_lzma_stream_flags_compare _lzma_stream_footer_decode _lzma_stream_footer_encode"
    "_lzma_stream_header_decode _lzma_stream_header_encode _lzma_version_number"
    "_lzma_version_string _lzma_vli_decode _lzma_vli_encode _lzma_vli_size"
).split()

_LIBRESOLV_9_SYMS = (
    "___res_9_p_cert_syms ___res_9_p_class_syms ___res_9_p_key_syms ___res_9_p_rcode_syms"
    "___res_9_p_type_syms ___res_9_state __res_9_h_errno_set __res_9_ns_flagdata"
    "_dns_all_server_addrs _dns_async_cancel _dns_async_handle_reply _dns_async_receive"
    "_dns_async_send _dns_async_start _dns_class_number _dns_class_string _dns_free"
    "_dns_free_question _dns_free_reply _dns_free_resource_record _dns_get_buffer_size"
    "_dns_lookup _dns_open _dns_parse_packet _dns_parse_question _dns_parse_resource_record"
    "_dns_print_handle _dns_print_question _dns_print_reply _dns_print_resource_record"
    "_dns_query _dns_search _dns_search_list_count _dns_search_list_domain"
    "_dns_server_list_address _dns_server_list_count _dns_set_buffer_size _dns_set_debug"
    "_dns_type_number _dns_type_string _res_9_b64_ntop _res_9_b64_pton _res_9_close"
    "_res_9_dn_comp _res_9_dn_count_labels _res_9_dn_expand _res_9_dn_skipname _res_9_dnok"
    "_res_9_findzonecut _res_9_findzonecut2 _res_9_fp_nquery _res_9_fp_query _res_9_fp_resstat"
    "_res_9_getlong _res_9_getservers _res_9_getshort _res_9_hnok _res_9_hostalias_1"
    "_res_9_hostalias_2 _res_9_init _res_9_isourserver _res_9_loc_aton _res_9_loc_ntoa"
    "_res_9_mailok _res_9_mkquery _res_9_nameinquery _res_9_nametoclass _res_9_nametotype"
    "_res_9_nclose _res_9_ndestroy _res_9_ninit _res_9_nisourserver _res_9_nmkquery _res_9_nopt"
    "_res_9_nopt_rdata _res_9_nquery _res_9_nquerydomain _res_9_nrandomid _res_9_ns_datetosecs"
    "_res_9_ns_find_tsig _res_9_ns_format_ttl _res_9_ns_get16 _res_9_ns_get32"
    "_res_9_ns_initparse _res_9_ns_makecanon _res_9_ns_msg_getflag _res_9_ns_name_compress"
    "_res_9_ns_name_ntol _res_9_ns_name_ntop _res_9_ns_name_pack _res_9_ns_name_pton"
    "_res_9_ns_name_pton2 _res_9_ns_name_rollback _res_9_ns_name_skip _res_9_ns_name_uncompress"
    "_res_9_ns_name_unpack _res_9_ns_name_unpack2 _res_9_ns_parse_ttl _res_9_ns_parserr"
    "_res_9_ns_parserr2 _res_9_ns_put16 _res_9_ns_put32 _res_9_ns_samedomain _res_9_ns_samename"
    "_res_9_ns_sign _res_9_ns_sign2 _res_9_ns_sign_tcp _res_9_ns_sign_tcp2"
    "_res_9_ns_sign_tcp_init _res_9_ns_skiprr _res_9_ns_sprintrr _res_9_ns_sprintrrf"
    "_res_9_ns_subdomain _res_9_ns_verify _res_9_ns_verify_tcp _res_9_ns_verify_tcp_init"
    "_res_9_nsearch _res_9_nsend _res_9_nsendsigned _res_9_ownok _res_9_p_cdname"
    "_res_9_p_cdnname _res_9_p_class _res_9_p_fqname _res_9_p_fqnname _res_9_p_option"
    "_res_9_p_query _res_9_p_rcode _res_9_p_secstodate _res_9_p_section _res_9_p_time"
    "_res_9_p_type _res_9_pquery _res_9_putlong _res_9_putshort _res_9_queriesmatch"
    "_res_9_query _res_9_querydomain _res_9_randomid _res_9_search _res_9_send"
    "_res_9_sendsigned _res_9_setservers _res_9_sym_ntop _res_9_sym_ntos _res_9_sym_ston"
    "_res_9_vinit _res_buildprotolist _res_destroyprotolist _res_destroyservicelist"
    "_res_get_bitstringsuffix _res_get_nibblesuffix _res_get_nibblesuffix2 _res_protocolname"
    "_res_servicename"
).split()

_LIBNCURSES_5_4_SYMS = (
    "_BC _COLORS _COLOR_PAIR _COLOR_PAIRS _COLS _ESCDELAY _LINES _PAIR_NUMBER _PC _SP _TABSIZE"
    "_UP __nc_abiver __nc_access __nc_add_to_try __nc_align_termtype __nc_basename"
    "__nc_baudrate __nc_build_wch __nc_capcmp __nc_captoinfo __nc_check_termtype"
    "__nc_check_termtype2 __nc_comment_end __nc_comment_start __nc_copy_entry"
    "__nc_copy_termtype __nc_curr_col __nc_curr_file_pos __nc_curr_line __nc_curr_token"
    "__nc_delink_entry __nc_disable_period __nc_do_color __nc_doalloc __nc_entry_match"
    "__nc_err_abort __nc_expand_try __nc_expanded __nc_fallback __nc_find_entry"
    "__nc_find_type_entry __nc_first_db __nc_first_name __nc_flush __nc_format_slks"
    "__nc_free_and_exit __nc_free_entries __nc_free_entry __nc_free_termtype __nc_freeall"
    "__nc_freewin __nc_get_alias_table __nc_get_hash_info __nc_get_hash_table __nc_get_locale"
    "__nc_get_screensize __nc_get_source __nc_get_table __nc_get_token __nc_get_tty_mode"
    "__nc_get_type __nc_getenv_num __nc_globals __nc_handle_sigwinch __nc_has_mouse"
    "__nc_hash_map __nc_head __nc_home_terminfo __nc_infotocap __nc_init_acs __nc_init_entry"
    "__nc_init_keytry __nc_init_termtype __nc_init_wacs __nc_insert_ch __nc_insert_wch"
    "__nc_is_abs_path __nc_is_charable __nc_is_dir_path __nc_is_file_path __nc_keep_tic_dir"
    "__nc_keyname __nc_keypad __nc_last_db __nc_leaks_tinfo __nc_locale_breaks_acs"
    "__nc_make_oldhash __nc_makenew __nc_merge_entry __nc_msec_cost __nc_mvcur __nc_mvcur_init"
    "__nc_mvcur_resume __nc_mvcur_wrap __nc_name_match __nc_next_db __nc_nulls_sent"
    "__nc_oldnums __nc_ospeed __nc_outch __nc_panelhook __nc_panic_mode __nc_parse_entry"
    "__nc_pathlast __nc_prescreen __nc_printf_string __nc_progname __nc_push_token __nc_putchar"
    "__nc_putp __nc_putp_flush __nc_read_entry __nc_read_entry_source __nc_read_file_entry"
    "__nc_read_termcap_entry __nc_read_termtype __nc_remove_key __nc_remove_string __nc_render"
    "__nc_reset_colors __nc_reset_input __nc_resolve_uses __nc_resolve_uses2 __nc_ripoffline"
    "__nc_rootname __nc_safe_strcat __nc_safe_strcpy __nc_save_str __nc_screen_chain"
    "__nc_screen_init __nc_screen_of __nc_screen_resume __nc_screen_wrap __nc_scroll_oldhash"
    "__nc_scroll_optimize __nc_scroll_window __nc_scrolln __nc_set_buffer __nc_set_no_padding"
    "__nc_set_source __nc_set_tty_mode __nc_set_type __nc_set_writedir __nc_setenv_num"
    "__nc_setup_tinfo __nc_setupscreen __nc_setupterm __nc_signal_handler __nc_slk_initialize"
    "__nc_start_line __nc_str_copy __nc_str_init __nc_str_null __nc_strict_bsd"
    "__nc_suppress_warnings __nc_synchook __nc_syntax __nc_syserr_abort __nc_tail __nc_tic_dir"
    "__nc_tic_expand __nc_tic_written __nc_timed_wait __nc_tinfo_cmdch __nc_tinfo_fkeys"
    "__nc_tiparm __nc_to_char __nc_to_widechar __nc_tparm_analyze __nc_tparm_err __nc_tracing"
    "__nc_trans_string __nc_trim_sgr0 __nc_unctrl __nc_ungetch __nc_unicode_locale"
    "__nc_update_screensize __nc_user_definable __nc_visbuf __nc_visbuf2 __nc_visbufn __nc_wacs"
    "__nc_waddch_nosync __nc_warning __nc_wchstrlen __nc_wcrtomb __nc_wgetch __nc_wrap_entry"
    "__nc_write_entry _acs_map _add_wch _add_wchnstr _add_wchstr _addch _addchnstr _addchstr"
    "_addnstr _addnwstr _addstr _addwstr _assume_default_colors _attr_get _attr_off _attr_on"
    "_attr_set _attroff _attron _attrset _baudrate _beep _bkgd _bkgdset _bkgrnd _bkgrndset"
    "_boolcodes _boolfnames _boolnames _border _border_set _box _box_set _can_change_color"
    "_cbreak _chgat _clear _clearok _clrtobot _clrtoeol _color_content _color_set _copywin"
    "_cur_term _curs_set _curscr _curses_version _def_prog_mode _def_shell_mode _define_key"
    "_del_curterm _delay_output _delch _deleteln _delscreen _delwin _derwin _doupdate _dupwin"
    "_echo _echo_wchar _echochar _endwin _erase _erasechar _erasewchar _filter _flash _flushinp"
    "_get_escdelay _get_wch _get_wstr _getattrs _getbegx _getbegy _getbkgd _getbkgrnd _getcchar"
    "_getch _getcurx _getcury _getmaxx _getmaxy _getmouse _getn_wstr _getnstr _getparx _getpary"
    "_getstr _getwin _halfdelay _has_colors _has_ic _has_il _has_key _has_mouse _hline"
    "_hline_set _idcok _idlok _immedok _in_wch _in_wchnstr _in_wchstr _inch _inchnstr _inchstr"
    "_init_color _init_pair _initscr _innstr _innwstr _ins_nwstr _ins_wch _ins_wstr _insch"
    "_insdelln _insertln _insnstr _insstr _instr _intrflush _inwstr _is_cleared _is_idcok"
    "_is_idlok _is_immedok _is_keypad _is_leaveok _is_linetouched _is_nodelay _is_notimeout"
    "_is_pad _is_scrollok _is_subwin _is_syncok _is_term_resized _is_wintouched _isendwin"
    "_key_defined _key_name _keybound _keyname _keyok _keypad _killchar _killwchar _leaveok"
    "_longname _mcprint _meta _mouse_trafo _mouseinterval _mousemask _move _mvadd_wch"
    "_mvadd_wchnstr _mvadd_wchstr _mvaddch _mvaddchnstr _mvaddchstr _mvaddnstr _mvaddnwstr"
    "_mvaddstr _mvaddwstr _mvchgat _mvcur _mvdelch _mvderwin _mvget_wch _mvget_wstr _mvgetch"
    "_mvgetn_wstr _mvgetnstr _mvgetstr _mvhline _mvhline_set _mvin_wch _mvin_wchnstr"
    "_mvin_wchstr _mvinch _mvinchnstr _mvinchstr _mvinnstr _mvinnwstr _mvins_nwstr _mvins_wch"
    "_mvins_wstr _mvinsch _mvinsnstr _mvinsstr _mvinstr _mvinwstr _mvprintw _mvscanw _mvvline"
    "_mvvline_set _mvwadd_wch _mvwadd_wchnstr _mvwadd_wchstr _mvwaddch _mvwaddchnstr"
    "_mvwaddchstr _mvwaddnstr _mvwaddnwstr _mvwaddstr _mvwaddwstr _mvwchgat _mvwdelch"
    "_mvwget_wch _mvwget_wstr _mvwgetch _mvwgetn_wstr _mvwgetnstr _mvwgetstr _mvwhline"
    "_mvwhline_set _mvwin _mvwin_wch _mvwin_wchnstr _mvwin_wchstr _mvwinch _mvwinchnstr"
    "_mvwinchstr _mvwinnstr _mvwinnwstr _mvwins_nwstr _mvwins_wch _mvwins_wstr _mvwinsch"
    "_mvwinsnstr _mvwinsstr _mvwinstr _mvwinwstr _mvwprintw _mvwscanw _mvwvline _mvwvline_set"
    "_napms _newpad _newscr _newterm _newwin _nl _nocbreak _nodelay _noecho _nofilter _nonl"
    "_noqiflush _noraw _notimeout _numcodes _numfnames _numnames _ospeed _overlay _overwrite"
    "_pair_content _pecho_wchar _pechochar _pnoutrefresh _prefresh _printw _putp _putwin"
    "_qiflush _raw _redrawwin _refresh _reset_prog_mode _reset_shell_mode _resetty _resize_term"
    "_resizeterm _restartterm _ripoffline _savetty _scanw _scr_dump _scr_init _scr_restore"
    "_scr_set _scrl _scroll _scrollok _set_curterm _set_escdelay _set_tabsize _set_term"
    "_setcchar _setscrreg _setupterm _slk_attr _slk_attr_off _slk_attr_on _slk_attr_set"
    "_slk_attroff _slk_attron _slk_attrset _slk_clear _slk_color _slk_init _slk_label"
    "_slk_noutrefresh _slk_refresh _slk_restore _slk_set _slk_touch _slk_wset _standend"
    "_standout _start_color _stdscr _strcodes _strfnames _strnames _subpad _subwin _syncok"
    "_term_attrs _termattrs _termname _tgetent _tgetflag _tgetnum _tgetstr _tgoto _tigetflag"
    "_tigetnum _tigetstr _timeout _tiparm _tiparm_s _touchline _touchwin _tparm _tputs _ttytype"
    "_typeahead _unctrl _unget_wch _ungetch _ungetmouse _untouchwin _use_default_colors"
    "_use_env _use_extended_names _use_legacy_coding _use_screen _use_tioctl _use_window"
    "_vid_attr _vid_puts _vidattr _vidputs _vline _vline_set _vw_printw _vw_scanw _vwprintw"
    "_vwscanw _wadd_wch _wadd_wchnstr _wadd_wchstr _waddch _waddchnstr _waddchstr _waddnstr"
    "_waddnwstr _waddstr _waddwstr _wattr_get _wattr_off _wattr_on _wattr_set _wattroff"
    "_wattron _wattrset _wbkgd _wbkgdset _wbkgrnd _wbkgrndset _wborder _wborder_set _wchgat"
    "_wclear _wclrtobot _wclrtoeol _wcolor_set _wcursyncup _wdelch _wdeleteln _wecho_wchar"
    "_wechochar _wenclose _werase _wget_wch _wget_wstr _wgetbkgrnd _wgetch _wgetdelay"
    "_wgetn_wstr _wgetnstr _wgetparent _wgetscrreg _wgetstr _whline _whline_set _win_wch"
    "_win_wchnstr _win_wchstr _winch _winchnstr _winchstr _winnstr _winnwstr _wins_nwstr"
    "_wins_wch _wins_wstr _winsch _winsdelln _winsertln _winsnstr _winsstr _winstr _winwstr"
    "_wmouse_trafo _wmove _wnoutrefresh _wprintw _wredrawln _wrefresh _wresize _wscanw _wscrl"
    "_wsetscrreg _wstandend _wstandout _wsyncdown _wsyncup _wtimeout _wtouchln _wunctrl _wvline"
    "_wvline_set"
).split()

_LIBEDIT_3_SYMS = (
    "__el_fn_complete __el_fn_sh_complete __rl_abort_internal"
    "__rl_print_completions_horizontally __rl_qsort_string_compare _add_history _clear_history"
    "_completion_matches _current_history _el_beep _el_deletestr _el_end _el_get _el_getc"
    "_el_gets _el_init _el_insertstr _el_line _el_parse _el_push _el_reset _el_resize _el_set"
    "_el_source _el_wget _el_wgetc _el_wgets _el_winsertstr _el_wline _el_wparse _el_wpush"
    "_el_wset _emacs_ctlx_keymap _emacs_meta_keymap _emacs_standard_keymap"
    "_filename_completion_function _get_history_event _history _history_arg_extract"
    "_history_base _history_end _history_expand _history_get _history_get_history_state"
    "_history_init _history_is_stifled _history_length _history_search _history_search_pos"
    "_history_search_prefix _history_set_pos _history_tokenize _history_total_bytes"
    "_history_truncate_file _history_w _history_wend _history_winit _max_input_history"
    "_next_history _previous_history _read_history _readline _readline_echoing_p"
    "_remove_history _replace_history_entry _rl_add_defun _rl_already_prompted"
    "_rl_attempted_completion_function _rl_attempted_completion_over"
    "_rl_basic_word_break_characters _rl_bind_key _rl_bind_key_in_map"
    "_rl_callback_handler_install _rl_callback_handler_remove _rl_callback_read_char"
    "_rl_cleanup_after_signal _rl_complete _rl_completer_quote_characters"
    "_rl_completer_word_break_characters _rl_completion_append_character"
    "_rl_completion_display_matches_hook _rl_completion_entry_function _rl_completion_matches"
    "_rl_completion_query_items _rl_completion_type _rl_completion_word_break_hook"
    "_rl_deprep_term_function _rl_deprep_terminal _rl_display_match_list _rl_end"
    "_rl_filename_completion_desired _rl_filename_completion_function _rl_forced_update_display"
    "_rl_free_line_state _rl_generic_bind _rl_get_keymap _rl_get_previous_history"
    "_rl_get_screen_size _rl_getc_function _rl_ignore_completion_duplicates"
    "_rl_inhibit_completion _rl_initialize _rl_insert _rl_insert_text _rl_instream"
    "_rl_kill_text _rl_library_version _rl_line_buffer _rl_make_bare_keymap _rl_newline"
    "_rl_on_new_line _rl_outstream _rl_parse_and_bind _rl_point _rl_pre_input_hook"
    "_rl_prep_term_function _rl_prep_terminal _rl_prompt _rl_read_init_file _rl_read_key"
    "_rl_readline_name _rl_readline_version _rl_redisplay _rl_redisplay_function"
    "_rl_reset_terminal _rl_set_keymap _rl_set_prompt _rl_set_screen_size _rl_special_prefixes"
    "_rl_startup_hook _rl_stuff_char _rl_terminal_name _rl_variable_bind _stifle_history"
    "_tilde_expand _tok_end _tok_init _tok_line _tok_reset _tok_str _tok_wend _tok_winit"
    "_tok_wline _tok_wreset _tok_wstr _unstifle_history _username_completion_function"
    "_using_history _where_history _write_history"
).split()

_LIBEXPAT_1_SYMS = (
    "_XML_DefaultCurrent _XML_ErrorString _XML_ExpatVersion _XML_ExpatVersionInfo"
    "_XML_ExternalEntityParserCreate _XML_FreeContentModel _XML_GetBase _XML_GetBuffer"
    "_XML_GetCurrentByteCount _XML_GetCurrentByteIndex _XML_GetCurrentColumnNumber"
    "_XML_GetCurrentLineNumber _XML_GetErrorCode _XML_GetFeatureList _XML_GetIdAttributeIndex"
    "_XML_GetInputContext _XML_GetParsingStatus _XML_GetSpecifiedAttributeCount _XML_MemFree"
    "_XML_MemMalloc _XML_MemRealloc _XML_Parse _XML_ParseBuffer _XML_ParserCreate"
    "_XML_ParserCreateNS _XML_ParserCreate_MM _XML_ParserFree _XML_ParserReset"
    "_XML_ResumeParser _XML_SetAttlistDeclHandler _XML_SetBase"
    "_XML_SetBillionLaughsAttackProtectionActivationThreshold"
    "_XML_SetBillionLaughsAttackProtectionMaximumAmplification _XML_SetCdataSectionHandler"
    "_XML_SetCharacterDataHandler _XML_SetCommentHandler _XML_SetDefaultHandler"
    "_XML_SetDefaultHandlerExpand _XML_SetDoctypeDeclHandler _XML_SetElementDeclHandler"
    "_XML_SetElementHandler _XML_SetEncoding _XML_SetEndCdataSectionHandler"
    "_XML_SetEndDoctypeDeclHandler _XML_SetEndElementHandler _XML_SetEndNamespaceDeclHandler"
    "_XML_SetEntityDeclHandler _XML_SetExternalEntityRefHandler"
    "_XML_SetExternalEntityRefHandlerArg _XML_SetHashSalt _XML_SetNamespaceDeclHandler"
    "_XML_SetNotStandaloneHandler _XML_SetNotationDeclHandler _XML_SetParamEntityParsing"
    "_XML_SetProcessingInstructionHandler _XML_SetReparseDeferralEnabled"
    "_XML_SetReturnNSTriplet _XML_SetSkippedEntityHandler _XML_SetStartCdataSectionHandler"
    "_XML_SetStartDoctypeDeclHandler _XML_SetStartElementHandler"
    "_XML_SetStartNamespaceDeclHandler _XML_SetUnknownEncodingHandler"
    "_XML_SetUnparsedEntityDeclHandler _XML_SetUserData _XML_SetXmlDeclHandler _XML_StopParser"
    "_XML_UseForeignDTD _XML_UseParserAsHandlerArg"
).split()

_LIBFORM_5_4_SYMS = (
    "_TYPE_ALNUM _TYPE_ALPHA _TYPE_ENUM _TYPE_INTEGER _TYPE_IPV4 _TYPE_NUMERIC _TYPE_REGEXP"
    "__nc_Copy_Argument __nc_Copy_Type __nc_Default_Field __nc_Default_FieldType"
    "__nc_Default_Form __nc_First_Active_Field __nc_Free_Argument __nc_Free_Type"
    "__nc_Internal_Validation __nc_Make_Argument __nc_Position_Form_Cursor"
    "__nc_Refresh_Current_Field __nc_Set_Current_Field __nc_Set_Form_Page"
    "__nc_Synchronize_Attributes __nc_Synchronize_Options __nc_Widen_String __nc_fty_generic"
    "__nc_get_fieldbuffer _current_field _data_ahead _data_behind _dup_field"
    "_dynamic_field_info _field_arg _field_back _field_buffer _field_count _field_fore"
    "_field_index _field_info _field_init _field_just _field_opts _field_opts_off"
    "_field_opts_on _field_pad _field_status _field_term _field_type _field_userptr"
    "_form_driver _form_driver_w _form_fields _form_init _form_opts _form_opts_off"
    "_form_opts_on _form_page _form_request_by_name _form_request_name _form_sub _form_term"
    "_form_userptr _form_win _free_field _free_fieldtype _free_form _link_field _link_fieldtype"
    "_move_field _new_field _new_fieldtype _new_form _new_page _pos_form_cursor _post_form"
    "_scale_form _set_current_field _set_field_back _set_field_buffer _set_field_fore"
    "_set_field_init _set_field_just _set_field_opts _set_field_pad _set_field_status"
    "_set_field_term _set_field_type _set_field_userptr _set_fieldtype_arg"
    "_set_fieldtype_choice _set_form_fields _set_form_init _set_form_opts _set_form_page"
    "_set_form_sub _set_form_term _set_form_userptr _set_form_win _set_max_field _set_new_page"
    "_unpost_form"
).split()

_LIBMENU_5_4_SYMS = (
    "__nc_Calculate_Item_Length_and_Width __nc_Calculate_Text_Width __nc_Connect_Items"
    "__nc_Default_Item __nc_Default_Menu __nc_Disconnect_Items __nc_Draw_Menu __nc_Link_Items"
    "__nc_Match_Next_Character_In_Item_Name __nc_New_TopRow_and_CurrentItem __nc_Post_Item"
    "__nc_Show_Menu __nc_menu_cursor_pos _current_item _free_item _free_menu _item_count"
    "_item_description _item_index _item_init _item_name _item_opts _item_opts_off"
    "_item_opts_on _item_term _item_userptr _item_value _item_visible _menu_back _menu_driver"
    "_menu_fore _menu_format _menu_grey _menu_init _menu_items _menu_mark _menu_opts"
    "_menu_opts_off _menu_opts_on _menu_pad _menu_pattern _menu_request_by_name"
    "_menu_request_name _menu_spacing _menu_sub _menu_term _menu_userptr _menu_win _new_item"
    "_new_menu _pos_menu_cursor _post_menu _scale_menu _set_current_item _set_item_init"
    "_set_item_opts _set_item_term _set_item_userptr _set_item_value _set_menu_back"
    "_set_menu_fore _set_menu_format _set_menu_grey _set_menu_init _set_menu_items"
    "_set_menu_mark _set_menu_opts _set_menu_pad _set_menu_pattern _set_menu_spacing"
    "_set_menu_sub _set_menu_term _set_menu_userptr _set_menu_win _set_top_row _top_row"
    "_unpost_menu"
).split()

_LIBPANEL_5_4_SYMS = (
    "_bottom_panel _del_panel _hide_panel _move_panel _new_panel _panel_above _panel_below"
    "_panel_hidden _panel_userptr _panel_window _replace_panel _set_panel_userptr _show_panel"
    "_top_panel _update_panels"
).split()

_LIBBSM_0_SYMS = (
    "_au_bsm_to_domain _au_bsm_to_errno _au_bsm_to_fcntl_cmd _au_bsm_to_socket_type _au_close"
    "_au_close_buffer _au_close_token _au_close_with_errors _au_domain_to_bsm _au_errno_to_bsm"
    "_au_fcntl_cmd_to_bsm _au_fetch_tok _au_free_token _au_get_state _au_notify_initialize"
    "_au_notify_terminate _au_open _au_poltostr _au_preselect _au_print_flags_tok _au_print_tok"
    "_au_print_tok_xml _au_print_xml_footer _au_print_xml_header _au_read_rec _au_sdev_close"
    "_au_sdev_fd _au_sdev_open _au_sdev_read_aia _au_sflagstostr _au_socket_type_to_bsm"
    "_au_strerror _au_strtopol _au_strtosflags _au_to_arg _au_to_arg32 _au_to_arg64"
    "_au_to_certificate_hash _au_to_data _au_to_exec_args _au_to_exec_env _au_to_exit"
    "_au_to_file _au_to_groups _au_to_header _au_to_header32 _au_to_header32_ex"
    "_au_to_header32_ex_tm _au_to_header32_tm _au_to_header64 _au_to_header64_tm"
    "_au_to_header_ex _au_to_identity _au_to_in_addr _au_to_in_addr_ex _au_to_ip _au_to_ipc"
    "_au_to_ipc_perm _au_to_iport _au_to_kevent _au_to_krb5_principal _au_to_me"
    "_au_to_newgroups _au_to_opaque _au_to_path _au_to_process _au_to_process32"
    "_au_to_process32_ex _au_to_process64 _au_to_process64_ex _au_to_process_ex _au_to_return"
    "_au_to_return32 _au_to_return64 _au_to_seq _au_to_sock_inet _au_to_sock_inet128"
    "_au_to_sock_inet32 _au_to_sock_unix _au_to_socket_ex _au_to_subject _au_to_subject32"
    "_au_to_subject32_ex _au_to_subject64 _au_to_subject64_ex _au_to_subject_ex _au_to_text"
    "_au_to_trailer _au_to_zonename _au_user_mask _au_write _audit_get_car _audit_get_class"
    "_audit_get_cond _audit_get_ctlmode _audit_get_cwd _audit_get_expire_after _audit_get_fsize"
    "_audit_get_kaudit _audit_get_kmask _audit_get_pinfo _audit_get_pinfo_addr"
    "_audit_get_policy _audit_get_qctrl _audit_get_sflags _audit_get_sflags_mask"
    "_audit_get_sinfo_addr _audit_get_stat _audit_send_trigger _audit_set_class _audit_set_cond"
    "_audit_set_fsize _audit_set_kaudit _audit_set_kmask _audit_set_pmask _audit_set_policy"
    "_audit_set_qctrl _audit_set_sflags _audit_set_sflags_mask _audit_set_stat"
    "_audit_set_terminal_id _audit_set_terminal_id_ex _audit_submit _audit_token_to_asid"
    "_audit_token_to_au32 _audit_token_to_auid _audit_token_to_egid _audit_token_to_euid"
    "_audit_token_to_pid _audit_token_to_pidversion _audit_token_to_rgid _audit_token_to_ruid"
    "_audit_write _audit_write_failure _audit_write_failure_ex _audit_write_failure_na"
    "_audit_write_failure_na_ex _audit_write_failure_self _audit_write_success"
    "_audit_write_success_ex _audit_write_success_self _cannot_audit _endac _endauclass"
    "_endauevent _endauuser _getacdir _getacexpire _getacfilesz _getacflg _getachost _getacmin"
    "_getacna _getacpol _getacsflagsmask _getauclassent _getauclassent_r _getauclassnam"
    "_getauclassnam_r _getauclassnum _getauclassnum_r _getauditflagsbin _getauditflagschar"
    "_getauevent _getauevent_r _getauevnam _getauevnam_r _getauevnonam _getauevnonam_r"
    "_getauevnum _getauevnum_r _getauuserent _getauuserent_r _getauusernam _getauusernam_r"
    "_getfauditflags _setac _setauclass _setauevent _setauuser"
).split()

_LIBCHARSET_1_SYMS = (
    "_libcharset_set_relocation_prefix _locale_charset"
).split()

_LIBXSLT_1_SYMS = (
    "_linkedOnOrAfterFall2023OSVersions _xslAddCall _xslDebugStatus _xslDropCall"
    "_xslHandleDebugger _xsltAddKey _xsltAddStackElemList _xsltAddTemplate _xsltAllocateExtra"
    "_xsltAllocateExtraCtxt _xsltApplyAttributeSet _xsltApplyImports _xsltApplyOneTemplate"
    "_xsltApplyStripSpaces _xsltApplyStylesheet _xsltApplyStylesheetUser _xsltApplyTemplates"
    "_xsltAttrListTemplateProcess _xsltAttrTemplateProcess _xsltAttrTemplateValueProcess"
    "_xsltAttrTemplateValueProcessNode _xsltAttribute _xsltCalibrateAdjust _xsltCallTemplate"
    "_xsltCheckExtPrefix _xsltCheckExtURI _xsltCheckRead _xsltCheckWrite _xsltChoose"
    "_xsltCleanupGlobals _xsltCleanupTemplates _xsltComment _xsltCompMatchClearCache"
    "_xsltCompileAttr _xsltCompilePattern _xsltComputeSortResult _xsltCopy _xsltCopyNamespace"
    "_xsltCopyNamespaceList _xsltCopyOf _xsltCopyTextString _xsltCreateRVT _xsltDebug"
    "_xsltDebugDumpExtensions _xsltDebugGetDefaultTrace _xsltDebugSetDefaultTrace"
    "_xsltDecimalFormatGetByName _xsltDecimalFormatGetByQName _xsltDefaultSortFunction"
    "_xsltDoSortFunction _xsltDocDefaultLoader _xsltDocumentComp _xsltDocumentElem"
    "_xsltDocumentFunction _xsltDocumentSortFunction _xsltElement _xsltElementAvailableFunction"
    "_xsltEngineVersion _xsltEvalAVT _xsltEvalAttrValueTemplate _xsltEvalGlobalVariables"
    "_xsltEvalOneUserParam _xsltEvalStaticAttrValueTemplate _xsltEvalTemplateString"
    "_xsltEvalUserParams _xsltEvalXPathPredicate _xsltEvalXPathString _xsltEvalXPathStringNs"
    "_xsltExtElementLookup _xsltExtMarker _xsltExtModuleElementLookup"
    "_xsltExtModuleElementPreComputeLookup _xsltExtModuleFunctionLookup"
    "_xsltExtModuleTopLevelLookup _xsltExtensionInstructionResultFinalize"
    "_xsltExtensionInstructionResultRegister _xsltFindDocument _xsltFindElemSpaceHandling"
    "_xsltFindTemplate _xsltFlagRVTs _xsltForEach _xsltFormatNumberConversion"
    "_xsltFormatNumberFunction _xsltFreeAVTList _xsltFreeAttributeSetsHashes"
    "_xsltFreeCompMatchList _xsltFreeCtxtExts _xsltFreeDocumentKeys _xsltFreeDocuments"
    "_xsltFreeExts _xsltFreeGlobalVariables _xsltFreeKeys _xsltFreeLocale _xsltFreeLocales"
    "_xsltFreeNamespaceAliasHashes _xsltFreeRVTs _xsltFreeSecurityPrefs _xsltFreeStackElemList"
    "_xsltFreeStyleDocuments _xsltFreeStylePreComps _xsltFreeStylesheet _xsltFreeTemplateHashes"
    "_xsltFreeTransformContext _xsltFunctionAvailableFunction _xsltFunctionNodeSet"
    "_xsltGenerateIdFunction _xsltGenericDebug _xsltGenericDebugContext _xsltGenericError"
    "_xsltGenericErrorContext _xsltGetCNsProp _xsltGetDebuggerStatus"
    "_xsltGetDefaultSecurityPrefs _xsltGetExtData _xsltGetExtInfo _xsltGetKey _xsltGetNamespace"
    "_xsltGetNsProp _xsltGetPlainNamespace _xsltGetProfileInformation _xsltGetQNameURI"
    "_xsltGetQNameURI2 _xsltGetSecurityPrefs _xsltGetSpecialNamespace _xsltGetTemplate"
    "_xsltGetUTF8Char _xsltGetXIncludeDefault _xsltIf _xsltInit _xsltInitAllDocKeys"
    "_xsltInitCtxtExts _xsltInitCtxtKey _xsltInitCtxtKeys _xsltInitElemPreComp _xsltInitGlobals"
    "_xsltIsBlank _xsltKeyFunction _xsltLibxmlVersion _xsltLibxsltVersion _xsltLoadDocument"
    "_xsltLoadStyleDocument _xsltLoadStylesheetPI _xsltLocalVariablePop _xsltLocalVariablePush"
    "_xsltLocaleStrcmp _xsltMaxDepth _xsltMaxVars _xsltMessage _xsltNamespaceAlias"
    "_xsltNeedElemSpaceHandling _xsltNewDocument _xsltNewElemPreComp _xsltNewLocale"
    "_xsltNewSecurityPrefs _xsltNewStyleDocument _xsltNewStylesheet _xsltNewTransformContext"
    "_xsltNextImport _xsltNormalizeCompSteps _xsltNumber _xsltNumberFormat"
    "_xsltParseGlobalParam _xsltParseGlobalVariable _xsltParseStylesheetAttributeSet"
    "_xsltParseStylesheetCallerParam _xsltParseStylesheetDoc _xsltParseStylesheetFile"
    "_xsltParseStylesheetImport _xsltParseStylesheetImportedDoc _xsltParseStylesheetInclude"
    "_xsltParseStylesheetOutput _xsltParseStylesheetParam _xsltParseStylesheetProcess"
    "_xsltParseStylesheetUser _xsltParseStylesheetVariable _xsltParseTemplateContent"
    "_xsltPreComputeExtModuleElement _xsltPrintErrorContext _xsltProcessOneNode"
    "_xsltProcessingInstruction _xsltProfileStylesheet _xsltQuoteOneUserParam"
    "_xsltQuoteUserParams _xsltRegisterAllElement _xsltRegisterAllExtras"
    "_xsltRegisterAllFunctions _xsltRegisterExtElement _xsltRegisterExtFunction"
    "_xsltRegisterExtModule _xsltRegisterExtModuleElement _xsltRegisterExtModuleFull"
    "_xsltRegisterExtModuleFunction _xsltRegisterExtModuleTopLevel _xsltRegisterExtPrefix"
    "_xsltRegisterExtras _xsltRegisterLocalRVT _xsltRegisterPersistRVT _xsltRegisterTestModule"
    "_xsltRegisterTmpRVT _xsltReleaseRVT _xsltReleaseRVTList _xsltResolveStylesheetAttributeSet"
    "_xsltRunStylesheet _xsltRunStylesheetUser _xsltSaveProfiling _xsltSaveResultTo"
    "_xsltSaveResultToFd _xsltSaveResultToFile _xsltSaveResultToFilename"
    "_xsltSaveResultToString _xsltSecurityAllow _xsltSecurityForbid _xsltSetCtxtParseOptions"
    "_xsltSetCtxtSecurityPrefs _xsltSetCtxtSortFunc _xsltSetDebuggerCallbacks"
    "_xsltSetDebuggerStatus _xsltSetDefaultSecurityPrefs _xsltSetGenericDebugFunc"
    "_xsltSetGenericErrorFunc _xsltSetLoaderFunc _xsltSetSecurityPrefs _xsltSetSortFunc"
    "_xsltSetTransformErrorFunc _xsltSetXIncludeDefault _xsltShutdownCtxtExts _xsltShutdownExts"
    "_xsltSort _xsltSplitQName _xsltStrxfrm _xsltStyleGetExtData _xsltStylePreCompute"
    "_xsltSystemPropertyFunction _xsltTemplateProcess _xsltTestCompMatchList _xsltText"
    "_xsltTimestamp _xsltTransformError _xsltUninit _xsltUnparsedEntityURIFunction"
    "_xsltUnregisterExtModule _xsltUnregisterExtModuleElement _xsltUnregisterExtModuleFunction"
    "_xsltUnregisterExtModuleTopLevel _xsltValueOf _xsltVariableLookup _xsltXPathCompile"
    "_xsltXPathCompileFlags _xsltXPathFunctionLookup _xsltXPathGetTransformContext"
    "_xsltXPathVariableLookup"
).split()

_LIBEXSLT_0_SYMS = (
    "_exsltCommonRegister _exsltDateRegister _exsltDateXpathCtxtRegister _exsltDynRegister"
    "_exsltFuncRegister _exsltLibexsltVersion _exsltLibraryVersion _exsltLibxmlVersion"
    "_exsltLibxsltVersion _exsltMathRegister _exsltMathXpathCtxtRegister _exsltRegisterAll"
    "_exsltSaxonRegister _exsltSetsRegister _exsltSetsXpathCtxtRegister _exsltStrRegister"
    "_exsltStrXpathCtxtRegister"
).split()

_LIBIPSEC_A_SYMS = (
    "___ipsec_errcode ___ipsec_set_strerror ___libipsec_create_buffer ___libipsec_delete_buffer"
    "___libipsec_flex_debug ___libipsec_flush_buffer ___libipsec_scan_buffer"
    "___libipsec_scan_bytes ___libipsec_scan_string ___libipsec_switch_to_buffer"
    "___libipsecalloc ___libipsecchar ___libipsecerror ___libipsecfree ___libipsecget_debug"
    "___libipsecget_in ___libipsecget_leng ___libipsecget_lineno ___libipsecget_out"
    "___libipsecget_text ___libipsecin ___libipsecleng ___libipseclex ___libipseclex_destroy"
    "___libipseclineno ___libipseclval ___libipsecnerrs ___libipsecout ___libipsecparse"
    "___libipsecpop_buffer_state ___libipsecpush_buffer_state ___libipsecrealloc"
    "___libipsecrestart ___libipsecset_debug ___libipsecset_in ___libipsecset_lineno"
    "___libipsecset_out ___libipsectext ___policy__strbuffer__free__"
    "___policy__strbuffer__init__ _ipsec_dump_policy _ipsec_dump_policy_withports"
    "_ipsec_get_policylen _ipsec_set_policy _ipsec_strerror"
).split()

_LIBUTIL_SYMS = (
    "_expand_number _freemntopts _getmnt_silent _getmntoptnum _getmntopts _getmntoptstr"
    "_humanize_number _pidfile_close _pidfile_open _pidfile_remove _pidfile_write _realhostname"
    "_realhostname_sa _reexec_to_match_kernel _reexec_to_match_lp64ness _tzlink _wipefs_alloc"
    "_wipefs_except_blocks _wipefs_free _wipefs_include_blocks _wipefs_wipe"
).split()

_LIBSANDBOX_1_SYMS = (
    "_SANDBOX_BUILD_ID _sandbox_apply _sandbox_apply_container _sandbox_compile_entitlements"
    "_sandbox_compile_file _sandbox_compile_named _sandbox_compile_string"
    "_sandbox_container_paths_iterate_items _sandbox_create_params"
    "_sandbox_exempt_from_network_approval_policy _sandbox_free_params _sandbox_free_profile"
    "_sandbox_inspect_pid _sandbox_inspect_smemory _sandbox_prepare_user_home_mount"
    "_sandbox_register_network_approval_policy_exemption_for_share _sandbox_register_profile"
    "_sandbox_register_sync_root _sandbox_set_param _sandbox_set_user_state_item"
    "_sandbox_set_user_state_item_with_persona _sandbox_unregister_all_profiles"
    "_sandbox_unregister_profile _sandbox_user_state_item_buffer_create"
    "_sandbox_user_state_item_buffer_destroy _sandbox_user_state_item_buffer_send"
    "_sandbox_user_state_iterate_items"
).split()

_LIBARCHIVE_2_SYMS = (
    "_archive_bzlib_version _archive_clear_error _archive_compression _archive_compression_name"
    "_archive_copy_error _archive_entry_acl _archive_entry_acl_add_entry"
    "_archive_entry_acl_add_entry_w _archive_entry_acl_clear _archive_entry_acl_count"
    "_archive_entry_acl_from_text _archive_entry_acl_from_text_w _archive_entry_acl_next"
    "_archive_entry_acl_reset _archive_entry_acl_text _archive_entry_acl_text_w"
    "_archive_entry_acl_to_text _archive_entry_acl_to_text_w _archive_entry_acl_types"
    "_archive_entry_atime _archive_entry_atime_is_set _archive_entry_atime_nsec"
    "_archive_entry_birthtime _archive_entry_birthtime_is_set _archive_entry_birthtime_nsec"
    "_archive_entry_clear _archive_entry_clone _archive_entry_copy_fflags_text"
    "_archive_entry_copy_fflags_text_w _archive_entry_copy_gname _archive_entry_copy_gname_w"
    "_archive_entry_copy_hardlink _archive_entry_copy_hardlink_w _archive_entry_copy_link"
    "_archive_entry_copy_link_w _archive_entry_copy_mac_metadata _archive_entry_copy_pathname"
    "_archive_entry_copy_pathname_w _archive_entry_copy_sourcepath"
    "_archive_entry_copy_sourcepath_w _archive_entry_copy_stat _archive_entry_copy_symlink"
    "_archive_entry_copy_symlink_w _archive_entry_copy_uname _archive_entry_copy_uname_w"
    "_archive_entry_ctime _archive_entry_ctime_is_set _archive_entry_ctime_nsec"
    "_archive_entry_dev _archive_entry_dev_is_set _archive_entry_devmajor"
    "_archive_entry_devminor _archive_entry_digest _archive_entry_fflags"
    "_archive_entry_fflags_text _archive_entry_filetype _archive_entry_filetype_is_set"
    "_archive_entry_free _archive_entry_gid _archive_entry_gid_is_set _archive_entry_gname"
    "_archive_entry_gname_utf8 _archive_entry_gname_w _archive_entry_hardlink"
    "_archive_entry_hardlink_utf8 _archive_entry_hardlink_w _archive_entry_ino"
    "_archive_entry_ino64 _archive_entry_ino_is_set _archive_entry_is_data_encrypted"
    "_archive_entry_is_encrypted _archive_entry_is_metadata_encrypted _archive_entry_linkify"
    "_archive_entry_linkresolver_free _archive_entry_linkresolver_new"
    "_archive_entry_linkresolver_set_strategy _archive_entry_mac_metadata _archive_entry_mode"
    "_archive_entry_mtime _archive_entry_mtime_is_set _archive_entry_mtime_nsec"
    "_archive_entry_new _archive_entry_new2 _archive_entry_nlink _archive_entry_partial_links"
    "_archive_entry_pathname _archive_entry_pathname_utf8 _archive_entry_pathname_w"
    "_archive_entry_perm _archive_entry_perm_is_set _archive_entry_rdev"
    "_archive_entry_rdevmajor _archive_entry_rdevminor _archive_entry_set_atime"
    "_archive_entry_set_birthtime _archive_entry_set_ctime _archive_entry_set_dev"
    "_archive_entry_set_devmajor _archive_entry_set_devminor _archive_entry_set_fflags"
    "_archive_entry_set_filetype _archive_entry_set_gid _archive_entry_set_gname"
    "_archive_entry_set_gname_utf8 _archive_entry_set_hardlink _archive_entry_set_hardlink_utf8"
    "_archive_entry_set_ino _archive_entry_set_ino64 _archive_entry_set_is_data_encrypted"
    "_archive_entry_set_is_metadata_encrypted _archive_entry_set_link"
    "_archive_entry_set_link_utf8 _archive_entry_set_mode _archive_entry_set_mtime"
    "_archive_entry_set_nlink _archive_entry_set_pathname _archive_entry_set_pathname_utf8"
    "_archive_entry_set_perm _archive_entry_set_rdev _archive_entry_set_rdevmajor"
    "_archive_entry_set_rdevminor _archive_entry_set_size _archive_entry_set_symlink"
    "_archive_entry_set_symlink_type _archive_entry_set_symlink_utf8 _archive_entry_set_uid"
    "_archive_entry_set_uname _archive_entry_set_uname_utf8 _archive_entry_size"
    "_archive_entry_size_is_set _archive_entry_sourcepath _archive_entry_sourcepath_w"
    "_archive_entry_sparse_add_entry _archive_entry_sparse_clear _archive_entry_sparse_count"
    "_archive_entry_sparse_next _archive_entry_sparse_reset _archive_entry_stat"
    "_archive_entry_strmode _archive_entry_symlink _archive_entry_symlink_type"
    "_archive_entry_symlink_utf8 _archive_entry_symlink_w _archive_entry_uid"
    "_archive_entry_uid_is_set _archive_entry_uname _archive_entry_uname_utf8"
    "_archive_entry_uname_w _archive_entry_unset_atime _archive_entry_unset_birthtime"
    "_archive_entry_unset_ctime _archive_entry_unset_mtime _archive_entry_unset_size"
    "_archive_entry_update_gname_utf8 _archive_entry_update_hardlink_utf8"
    "_archive_entry_update_link_utf8 _archive_entry_update_pathname_utf8"
    "_archive_entry_update_symlink_utf8 _archive_entry_update_uname_utf8"
    "_archive_entry_xattr_add_entry _archive_entry_xattr_clear _archive_entry_xattr_count"
    "_archive_entry_xattr_next _archive_entry_xattr_reset _archive_errno _archive_error_string"
    "_archive_file_count _archive_filter_bytes _archive_filter_code _archive_filter_count"
    "_archive_filter_name _archive_format _archive_format_name _archive_free"
    "_archive_liblz4_version _archive_liblzma_version _archive_libzstd_version"
    "_archive_match_exclude_entry _archive_match_exclude_pattern"
    "_archive_match_exclude_pattern_from_file _archive_match_exclude_pattern_from_file_w"
    "_archive_match_exclude_pattern_w _archive_match_excluded _archive_match_free"
    "_archive_match_include_date _archive_match_include_date_w _archive_match_include_file_time"
    "_archive_match_include_file_time_w _archive_match_include_gid _archive_match_include_gname"
    "_archive_match_include_gname_w _archive_match_include_pattern"
    "_archive_match_include_pattern_from_file _archive_match_include_pattern_from_file_w"
    "_archive_match_include_pattern_w _archive_match_include_time _archive_match_include_uid"
    "_archive_match_include_uname _archive_match_include_uname_w _archive_match_new"
    "_archive_match_owner_excluded _archive_match_path_excluded"
    "_archive_match_path_unmatched_inclusions _archive_match_path_unmatched_inclusions_next"
    "_archive_match_path_unmatched_inclusions_next_w _archive_match_set_inclusion_recursion"
    "_archive_match_time_excluded _archive_position_compressed _archive_position_uncompressed"
    "_archive_read_add_callback_data _archive_read_add_passphrase"
    "_archive_read_append_callback_data _archive_read_append_filter"
    "_archive_read_append_filter_program _archive_read_append_filter_program_signature"
    "_archive_read_close _archive_read_data _archive_read_data_block _archive_read_data_into_fd"
    "_archive_read_data_skip _archive_read_disk_can_descend"
    "_archive_read_disk_current_filesystem _archive_read_disk_current_filesystem_is_remote"
    "_archive_read_disk_current_filesystem_is_synthetic _archive_read_disk_descend"
    "_archive_read_disk_entry_from_file _archive_read_disk_gname _archive_read_disk_new"
    "_archive_read_disk_open _archive_read_disk_open_w _archive_read_disk_set_atime_restored"
    "_archive_read_disk_set_behavior _archive_read_disk_set_gname_lookup"
    "_archive_read_disk_set_matching _archive_read_disk_set_metadata_filter_callback"
    "_archive_read_disk_set_standard_lookup _archive_read_disk_set_symlink_hybrid"
    "_archive_read_disk_set_symlink_logical _archive_read_disk_set_symlink_physical"
    "_archive_read_disk_set_uname_lookup _archive_read_disk_uname _archive_read_extract"
    "_archive_read_extract2 _archive_read_extract_set_progress_callback"
    "_archive_read_extract_set_skip_file _archive_read_finish _archive_read_format_capabilities"
    "_archive_read_free _archive_read_has_encrypted_entries _archive_read_header_position"
    "_archive_read_new _archive_read_next_header _archive_read_next_header2 _archive_read_open"
    "_archive_read_open1 _archive_read_open2 _archive_read_open_FILE _archive_read_open_fd"
    "_archive_read_open_file _archive_read_open_filename _archive_read_open_filename_w"
    "_archive_read_open_filenames _archive_read_open_memory _archive_read_open_memory2"
    "_archive_read_prepend_callback_data _archive_read_set_callback_data"
    "_archive_read_set_callback_data2 _archive_read_set_close_callback"
    "_archive_read_set_filter_option _archive_read_set_format _archive_read_set_format_option"
    "_archive_read_set_open_callback _archive_read_set_option _archive_read_set_options"
    "_archive_read_set_passphrase_callback _archive_read_set_read_callback"
    "_archive_read_set_seek_callback _archive_read_set_skip_callback"
    "_archive_read_set_switch_callback _archive_read_support_compression_all"
    "_archive_read_support_compression_bzip2 _archive_read_support_compression_compress"
    "_archive_read_support_compression_gzip _archive_read_support_compression_lzip"
    "_archive_read_support_compression_lzma _archive_read_support_compression_none"
    "_archive_read_support_compression_program"
    "_archive_read_support_compression_program_signature _archive_read_support_compression_rpm"
    "_archive_read_support_compression_uu _archive_read_support_compression_xz"
    "_archive_read_support_filter_all _archive_read_support_filter_by_code"
    "_archive_read_support_filter_bzip2 _archive_read_support_filter_compress"
    "_archive_read_support_filter_grzip _archive_read_support_filter_gzip"
    "_archive_read_support_filter_lrzip _archive_read_support_filter_lz4"
    "_archive_read_support_filter_lzip _archive_read_support_filter_lzma"
    "_archive_read_support_filter_lzop _archive_read_support_filter_none"
    "_archive_read_support_filter_program _archive_read_support_filter_program_signature"
    "_archive_read_support_filter_rpm _archive_read_support_filter_uu"
    "_archive_read_support_filter_xz _archive_read_support_filter_zstd"
    "_archive_read_support_format_7zip _archive_read_support_format_all"
    "_archive_read_support_format_ar _archive_read_support_format_by_code"
    "_archive_read_support_format_cab _archive_read_support_format_cpio"
    "_archive_read_support_format_empty _archive_read_support_format_gnutar"
    "_archive_read_support_format_iso9660 _archive_read_support_format_lha"
    "_archive_read_support_format_mtree _archive_read_support_format_rar"
    "_archive_read_support_format_rar5 _archive_read_support_format_raw"
    "_archive_read_support_format_tar _archive_read_support_format_warc"
    "_archive_read_support_format_xar _archive_read_support_format_zip"
    "_archive_read_support_format_zip_seekable _archive_read_support_format_zip_streamable"
    "_archive_seek_data _archive_set_error _archive_utility_string_sort"
    "_archive_version_details _archive_version_number _archive_version_string"
    "_archive_write_add_filter _archive_write_add_filter_b64encode"
    "_archive_write_add_filter_by_name _archive_write_add_filter_bzip2"
    "_archive_write_add_filter_compress _archive_write_add_filter_grzip"
    "_archive_write_add_filter_gzip _archive_write_add_filter_lrzip"
    "_archive_write_add_filter_lz4 _archive_write_add_filter_lzip"
    "_archive_write_add_filter_lzma _archive_write_add_filter_lzop"
    "_archive_write_add_filter_none _archive_write_add_filter_program"
    "_archive_write_add_filter_uuencode _archive_write_add_filter_xz"
    "_archive_write_add_filter_zstd _archive_write_close _archive_write_data"
    "_archive_write_data_block _archive_write_disk_gid _archive_write_disk_new"
    "_archive_write_disk_set_group_lookup _archive_write_disk_set_options"
    "_archive_write_disk_set_skip_file _archive_write_disk_set_standard_lookup"
    "_archive_write_disk_set_user_lookup _archive_write_disk_uid _archive_write_fail"
    "_archive_write_finish _archive_write_finish_entry _archive_write_free"
    "_archive_write_get_bytes_in_last_block _archive_write_get_bytes_per_block"
    "_archive_write_header _archive_write_new _archive_write_open _archive_write_open2"
    "_archive_write_open_FILE _archive_write_open_fd _archive_write_open_file"
    "_archive_write_open_filename _archive_write_open_filename_w _archive_write_open_memory"
    "_archive_write_set_bytes_in_last_block _archive_write_set_bytes_per_block"
    "_archive_write_set_compression_bzip2 _archive_write_set_compression_compress"
    "_archive_write_set_compression_gzip _archive_write_set_compression_lzip"
    "_archive_write_set_compression_lzma _archive_write_set_compression_none"
    "_archive_write_set_compression_program _archive_write_set_compression_xz"
    "_archive_write_set_filter_option _archive_write_set_format _archive_write_set_format_7zip"
    "_archive_write_set_format_ar_bsd _archive_write_set_format_ar_svr4"
    "_archive_write_set_format_by_name _archive_write_set_format_cpio"
    "_archive_write_set_format_cpio_bin _archive_write_set_format_cpio_newc"
    "_archive_write_set_format_cpio_odc _archive_write_set_format_cpio_pwb"
    "_archive_write_set_format_filter_by_ext _archive_write_set_format_filter_by_ext_def"
    "_archive_write_set_format_gnutar _archive_write_set_format_iso9660"
    "_archive_write_set_format_mtree _archive_write_set_format_mtree_classic"
    "_archive_write_set_format_option _archive_write_set_format_pax"
    "_archive_write_set_format_pax_restricted _archive_write_set_format_raw"
    "_archive_write_set_format_shar _archive_write_set_format_shar_dump"
    "_archive_write_set_format_ustar _archive_write_set_format_v7tar"
    "_archive_write_set_format_warc _archive_write_set_format_xar _archive_write_set_format_zip"
    "_archive_write_set_option _archive_write_set_options _archive_write_set_passphrase"
    "_archive_write_set_passphrase_callback _archive_write_set_skip_file"
    "_archive_write_zip_set_compression_deflate _archive_write_zip_set_compression_store"
    "_archive_zlib_version"
).split()


_SYSTEM_LIBRARIES: list[tuple[str, str, list[str], list[str]]] = [
    ("libz.1", "/usr/lib/libz.1.dylib", ['libz'], _LIBZ_1_SYMS),
    ("libsqlite3", "/usr/lib/libsqlite3.dylib", [], _LIBSQLITE3_SYMS),
    ("libxml2.2", "/usr/lib/libxml2.2.dylib", ['libxml2'], _LIBXML2_2_SYMS),
    ("libiconv.2", "/usr/lib/libiconv.2.dylib", ['libiconv'], _LIBICONV_2_SYMS),
    ("libcompression", "/usr/lib/libcompression.dylib", [], _LIBCOMPRESSION_SYMS),
    ("libbz2.1.0", "/usr/lib/libbz2.1.0.dylib", ['libbz2'], _LIBBZ2_1_0_SYMS),
    ("liblzma.5", "/usr/lib/liblzma.5.dylib", ['liblzma'], _LIBLZMA_5_SYMS),
    ("libresolv.9", "/usr/lib/libresolv.9.dylib", ['libresolv'], _LIBRESOLV_9_SYMS),
    ("libncurses.5.4", "/usr/lib/libncurses.5.4.dylib", ['libncurses', 'libcurses'], _LIBNCURSES_5_4_SYMS),
    ("libedit.3", "/usr/lib/libedit.3.dylib", ['libedit'], _LIBEDIT_3_SYMS),
    ("libexpat.1", "/usr/lib/libexpat.1.dylib", ['libexpat'], _LIBEXPAT_1_SYMS),
    ("libform.5.4", "/usr/lib/libform.5.4.dylib", ['libform'], _LIBFORM_5_4_SYMS),
    ("libmenu.5.4", "/usr/lib/libmenu.5.4.dylib", ['libmenu'], _LIBMENU_5_4_SYMS),
    ("libpanel.5.4", "/usr/lib/libpanel.5.4.dylib", ['libpanel'], _LIBPANEL_5_4_SYMS),
    ("libbsm.0", "/usr/lib/libbsm.0.dylib", ['libbsm'], _LIBBSM_0_SYMS),
    ("libcharset.1", "/usr/lib/libcharset.1.dylib", ['libcharset'], _LIBCHARSET_1_SYMS),
    ("libxslt.1", "/usr/lib/libxslt.1.dylib", ['libxslt'], _LIBXSLT_1_SYMS),
    ("libexslt.0", "/usr/lib/libexslt.0.dylib", ['libexslt'], _LIBEXSLT_0_SYMS),
    ("libipsec.A", "/usr/lib/libipsec.A.dylib", ['libipsec'], _LIBIPSEC_A_SYMS),
    ("libutil", "/usr/lib/libutil.dylib", [], _LIBUTIL_SYMS),
    ("libsandbox.1", "/usr/lib/libsandbox.1.dylib", ['libsandbox'], _LIBSANDBOX_1_SYMS),
    ("libarchive.2", "/usr/lib/libarchive.2.dylib", ['libarchive'], _LIBARCHIVE_2_SYMS),
    # ── Install-name-only TBDs (no exported symbols needed) ──
    ("libicucore.A", "/usr/lib/libicucore.A.dylib", ['libicucore'], []),
    ("libnetwork", "/usr/lib/libnetwork.dylib", [], []),
    ("libAppleArchive", "/usr/lib/libAppleArchive.dylib", [], []),
    ("libsqlite3.0", "/usr/lib/libsqlite3.0.dylib", [], []),
]


# ── Swift overlay libraries ────────────────────────────────────────
# Install-name-only TBDs (Swift mangled symbols are impractical to
# embed; runtime resolution handles them).

_SWIFT_LIBRARIES: list[tuple[str, str]] = [
    ("libswiftCore", "/usr/lib/swift/libswiftCore.dylib"),
    ("libswiftFoundation", "/usr/lib/swift/libswiftFoundation.dylib"),
    ("libswiftDarwin", "/usr/lib/swift/libswiftDarwin.dylib"),
    ("libswiftDispatch", "/usr/lib/swift/libswiftDispatch.dylib"),
    ("libswiftObjectiveC", "/usr/lib/swift/libswiftObjectiveC.dylib"),
    ("libswiftCoreFoundation", "/usr/lib/swift/libswiftCoreFoundation.dylib"),
    ("libswiftCoreGraphics", "/usr/lib/swift/libswiftCoreGraphics.dylib"),
    ("libswiftCoreImage", "/usr/lib/swift/libswiftCoreImage.dylib"),
    ("libswiftCoreLocation", "/usr/lib/swift/libswiftCoreLocation.dylib"),
    ("libswiftCoreMedia", "/usr/lib/swift/libswiftCoreMedia.dylib"),
    ("libswiftCoreData", "/usr/lib/swift/libswiftCoreData.dylib"),
    ("libswiftCoreAudio", "/usr/lib/swift/libswiftCoreAudio.dylib"),
    ("libswiftCoreMIDI", "/usr/lib/swift/libswiftCoreMIDI.dylib"),
    ("libswiftCoreML", "/usr/lib/swift/libswiftCoreML.dylib"),
    ("libswiftCoreNFC", "/usr/lib/swift/libswiftCoreNFC.dylib"),
    ("libswiftCryptoTokenKit", "/usr/lib/swift/libswiftCryptoTokenKit.dylib"),
    ("libswiftMetal", "/usr/lib/swift/libswiftMetal.dylib"),
    ("libswiftMetalKit", "/usr/lib/swift/libswiftMetalKit.dylib"),
    ("libswiftUIKit", "/usr/lib/swift/libswiftUIKit.dylib"),
    ("libswiftAVFoundation", "/usr/lib/swift/libswiftAVFoundation.dylib"),
    ("libswiftARKit", "/usr/lib/swift/libswiftARKit.dylib"),
    ("libswiftAccelerate", "/usr/lib/swift/libswiftAccelerate.dylib"),
    ("libswiftAppleArchive", "/usr/lib/swift/libswiftAppleArchive.dylib"),
    ("libswiftAssetsLibrary", "/usr/lib/swift/libswiftAssetsLibrary.dylib"),
    ("libswiftCallKit", "/usr/lib/swift/libswiftCallKit.dylib"),
    ("libswiftCarPlay", "/usr/lib/swift/libswiftCarPlay.dylib"),
    ("libswiftCloudKit", "/usr/lib/swift/libswiftCloudKit.dylib"),
    ("libswiftCompatibilitySpan", "/usr/lib/swift/libswiftCompatibilitySpan.dylib"),
    ("libswiftCompression", "/usr/lib/swift/libswiftCompression.dylib"),
    ("libswiftContacts", "/usr/lib/swift/libswiftContacts.dylib"),
    ("libswiftDataDetection", "/usr/lib/swift/libswiftDataDetection.dylib"),
    ("libswiftDemangle", "/usr/lib/swift/libswiftDemangle.dylib"),
    ("libswiftDistributed", "/usr/lib/swift/libswiftDistributed.dylib"),
    ("libswiftExtensionFoundation", "/usr/lib/swift/libswiftExtensionFoundation.dylib"),
    ("libswiftExtensionKit", "/usr/lib/swift/libswiftExtensionKit.dylib"),
    ("libswiftFileProvider", "/usr/lib/swift/libswiftFileProvider.dylib"),
    ("libswiftGameplayKit", "/usr/lib/swift/libswiftGameplayKit.dylib"),
    ("libswiftGLKit", "/usr/lib/swift/libswiftGLKit.dylib"),
    ("libswiftHealthKit", "/usr/lib/swift/libswiftHealthKit.dylib"),
    ("libswiftHomeKit", "/usr/lib/swift/libswiftHomeKit.dylib"),
    ("libswiftIdentityLookup", "/usr/lib/swift/libswiftIdentityLookup.dylib"),
    ("libswiftIntents", "/usr/lib/swift/libswiftIntents.dylib"),
    ("libswiftMapKit", "/usr/lib/swift/libswiftMapKit.dylib"),
    ("libswiftMediaPlayer", "/usr/lib/swift/libswiftMediaPlayer.dylib"),
    ("libswiftMetricKit", "/usr/lib/swift/libswiftMetricKit.dylib"),
    ("libswiftMLCompute", "/usr/lib/swift/libswiftMLCompute.dylib"),
    ("libswiftModelIO", "/usr/lib/swift/libswiftModelIO.dylib"),
    ("libswiftNaturalLanguage", "/usr/lib/swift/libswiftNaturalLanguage.dylib"),
    ("libswiftNearbyInteraction", "/usr/lib/swift/libswiftNearbyInteraction.dylib"),
    ("libswiftNetwork", "/usr/lib/swift/libswiftNetwork.dylib"),
    ("libswiftObservation", "/usr/lib/swift/libswiftObservation.dylib"),
    ("libswiftOSLog", "/usr/lib/swift/libswiftOSLog.dylib"),
    ("libswiftos", "/usr/lib/swift/libswiftos.dylib"),
    ("libswiftPassKit", "/usr/lib/swift/libswiftPassKit.dylib"),
    ("libswiftPencilKit", "/usr/lib/swift/libswiftPencilKit.dylib"),
    ("libswiftPhotos", "/usr/lib/swift/libswiftPhotos.dylib"),
    ("libswiftPhotosUI", "/usr/lib/swift/libswiftPhotosUI.dylib"),
    ("libswiftQuartzCore", "/usr/lib/swift/libswiftQuartzCore.dylib"),
    ("libswiftQuickLook", "/usr/lib/swift/libswiftQuickLook.dylib"),
    ("libswiftRegexBuilder", "/usr/lib/swift/libswiftRegexBuilder.dylib"),
    ("libswiftRemoteMirror", "/usr/lib/swift/libswiftRemoteMirror.dylib"),
    ("libswiftSceneKit", "/usr/lib/swift/libswiftSceneKit.dylib"),
    ("libswiftShazamKit", "/usr/lib/swift/libswiftShazamKit.dylib"),
    ("libswiftSoundAnalysis", "/usr/lib/swift/libswiftSoundAnalysis.dylib"),
    ("libswiftSoundAnalysis_Private", "/usr/lib/swift/libswiftSoundAnalysis_Private.dylib"),
    ("libswiftSpatial", "/usr/lib/swift/libswiftSpatial.dylib"),
    ("libswiftSpeech", "/usr/lib/swift/libswiftSpeech.dylib"),
    ("libswiftSpriteKit", "/usr/lib/swift/libswiftSpriteKit.dylib"),
    ("libswiftSwiftOnoneSupport", "/usr/lib/swift/libswiftSwiftOnoneSupport.dylib"),
    ("libswiftSynchronization", "/usr/lib/swift/libswiftSynchronization.dylib"),
    ("libswiftSystem", "/usr/lib/swift/libswiftSystem.dylib"),
    ("libswiftSystem_Foundation", "/usr/lib/swift/libswiftSystem_Foundation.dylib"),
    ("libswiftUniformTypeIdentifiers", "/usr/lib/swift/libswiftUniformTypeIdentifiers.dylib"),
    ("libswiftVideoToolbox", "/usr/lib/swift/libswiftVideoToolbox.dylib"),
    ("libswiftVision", "/usr/lib/swift/libswiftVision.dylib"),
    ("libswiftXPC", "/usr/lib/swift/libswiftXPC.dylib"),
    ("libswiftsimd", "/usr/lib/swift/libswiftsimd.dylib"),
    ("libswift_Concurrency", "/usr/lib/swift/libswift_Concurrency.dylib"),
    ("libswift_StringProcessing", "/usr/lib/swift/libswift_StringProcessing.dylib"),
    ("libswift_RegexParser", "/usr/lib/swift/libswift_RegexParser.dylib"),
    ("libswift_Builtin_float", "/usr/lib/swift/libswift_Builtin_float.dylib"),
    ("libswift_Volatile", "/usr/lib/swift/libswift_Volatile.dylib"),
    ("libswift_DarwinFoundation1", "/usr/lib/swift/libswift_DarwinFoundation1.dylib"),
    ("libswift_DarwinFoundation2", "/usr/lib/swift/libswift_DarwinFoundation2.dylib"),
    ("libswift_DarwinFoundation3", "/usr/lib/swift/libswift_DarwinFoundation3.dylib"),
    ("libswift_errno", "/usr/lib/swift/libswift_errno.dylib"),
    ("libswift_math", "/usr/lib/swift/libswift_math.dylib"),
    ("libswift_signal", "/usr/lib/swift/libswift_signal.dylib"),
    ("libswift_stdio", "/usr/lib/swift/libswift_stdio.dylib"),
    ("libswift_time", "/usr/lib/swift/libswift_time.dylib"),
    ("libswiftunistd", "/usr/lib/swift/libswiftunistd.dylib"),
    ("libswiftsys_time", "/usr/lib/swift/libswiftsys_time.dylib"),
]


def install_system_lib_stubs(
    sdk_root: Path,
    tbd_targets: list[str],
    include_swift: bool = False,
) -> None:
    """Generate TBD stubs for public system libraries."""
    usr_lib = sdk_root / "usr" / "lib"
    usr_lib.mkdir(parents=True, exist_ok=True)

    targets_str = ", ".join(tbd_targets)
    generated = 0

    for name, install_name, aliases, symbols in _SYSTEM_LIBRARIES:
        tbd_path = usr_lib / f"{name}.tbd"
        # Skip if already generated by libc.py or libcxx.py
        if tbd_path.exists():
            continue

        _write_tbd(tbd_path, install_name, targets_str, symbols)
        generated += 1

        # Generate unversioned alias TBDs that re-export the versioned lib
        for alias in aliases:
            alias_path = usr_lib / f"{alias}.tbd"
            if not alias_path.exists():
                _write_reexport_tbd(alias_path, install_name, targets_str)
                generated += 1

    # Common aliases that re-export from libSystem.B
    _LIBSYSTEM_ALIASES = [
        ("libpthread", "/usr/lib/libpthread.dylib"),
        ("libdl", "/usr/lib/libdl.dylib"),
        ("libm", "/usr/lib/libm.dylib"),
        ("libSystem", "/usr/lib/libSystem.dylib"),
    ]
    for alias_name, alias_install_name in _LIBSYSTEM_ALIASES:
        alias_path = usr_lib / f"{alias_name}.tbd"
        if not alias_path.exists():
            _write_reexport_tbd(alias_path, "/usr/lib/libSystem.B.dylib", targets_str)
            generated += 1

    # libc++.1 alias (linker may look for versioned name)
    libcxx1 = usr_lib / "libc++.1.tbd"
    if not libcxx1.exists():
        _write_reexport_tbd(libcxx1, "/usr/lib/libc++.1.dylib", targets_str)
        generated += 1

    # Re-export aliases for compatibility libraries
    _REEXPORT_ALIASES = [
        ("libtermcap", "/usr/lib/libncurses.5.4.dylib"),
        ("libreadline", "/usr/lib/libedit.3.dylib"),
        ("libcurses", "/usr/lib/libncurses.5.4.dylib"),
    ]
    for alias_name, reexport_target in _REEXPORT_ALIASES:
        alias_path = usr_lib / f"{alias_name}.tbd"
        if not alias_path.exists():
            _write_reexport_tbd(alias_path, reexport_target, targets_str)
            generated += 1

    if include_swift:
        swift_dir = usr_lib / "swift"
        swift_dir.mkdir(parents=True, exist_ok=True)
        for name, install_name in _SWIFT_LIBRARIES:
            tbd_path = swift_dir / f"{name}.tbd"
            if not tbd_path.exists():
                _write_tbd(
                    tbd_path, install_name, targets_str, [],
                    swift_abi_version=7,
                )
                generated += 1

    logger.info("Generated %d system library TBD stubs", generated)


def _write_tbd(
    path: Path,
    install_name: str,
    targets_str: str,
    symbols: list[str],
    swift_abi_version: int | None = None,
) -> None:
    """Write a TBD v4 stub file."""
    parts = [
        "--- !tapi-tbd",
        "tbd-version:     4",
        f"targets:         [{targets_str}]",
        f"install-name:    '{install_name}'",
    ]
    if swift_abi_version is not None:
        parts.append(f"swift-abi-version: {swift_abi_version}")
    if symbols:
        parts.append("exports:")
        parts.append(f"  - targets:     [{targets_str}]")
        parts.append("    symbols:")
        for sym in symbols:
            parts.append(f"      - {sym}")
    parts.append("...")
    parts.append("")
    path.write_text("\n".join(parts))


def _write_reexport_tbd(
    path: Path,
    reexport_install_name: str,
    targets_str: str,
) -> None:
    """Write a TBD v4 stub that re-exports another library."""
    alias_name = "/usr/lib/" + path.stem + ".dylib"
    path.write_text(
        f"--- !tapi-tbd\n"
        f"tbd-version:     4\n"
        f"targets:         [{targets_str}]\n"
        f"install-name:    '{alias_name}'\n"
        f"reexported-libraries:\n"
        f"  - targets:     [{targets_str}]\n"
        f"    libraries:\n"
        f"      - '{reexport_install_name}'\n"
        f"...\n"
    )

