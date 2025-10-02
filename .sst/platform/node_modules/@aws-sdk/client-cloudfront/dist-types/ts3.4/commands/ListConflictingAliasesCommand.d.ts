import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListConflictingAliasesRequest,
  ListConflictingAliasesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListConflictingAliasesCommandInput
  extends ListConflictingAliasesRequest {}
export interface ListConflictingAliasesCommandOutput
  extends ListConflictingAliasesResult,
    __MetadataBearer {}
export declare class ListConflictingAliasesCommand extends $Command<
  ListConflictingAliasesCommandInput,
  ListConflictingAliasesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListConflictingAliasesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListConflictingAliasesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListConflictingAliasesCommandInput,
    ListConflictingAliasesCommandOutput
  >;
  private serialize;
  private deserialize;
}
