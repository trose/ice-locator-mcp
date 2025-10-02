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
  ListOriginAccessControlsRequest,
  ListOriginAccessControlsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListOriginAccessControlsCommandInput
  extends ListOriginAccessControlsRequest {}
export interface ListOriginAccessControlsCommandOutput
  extends ListOriginAccessControlsResult,
    __MetadataBearer {}
export declare class ListOriginAccessControlsCommand extends $Command<
  ListOriginAccessControlsCommandInput,
  ListOriginAccessControlsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListOriginAccessControlsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListOriginAccessControlsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListOriginAccessControlsCommandInput,
    ListOriginAccessControlsCommandOutput
  >;
  private serialize;
  private deserialize;
}
