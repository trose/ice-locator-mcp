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
  GetOriginAccessControlRequest,
  GetOriginAccessControlResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetOriginAccessControlCommandInput
  extends GetOriginAccessControlRequest {}
export interface GetOriginAccessControlCommandOutput
  extends GetOriginAccessControlResult,
    __MetadataBearer {}
export declare class GetOriginAccessControlCommand extends $Command<
  GetOriginAccessControlCommandInput,
  GetOriginAccessControlCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetOriginAccessControlCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetOriginAccessControlCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetOriginAccessControlCommandInput,
    GetOriginAccessControlCommandOutput
  >;
  private serialize;
  private deserialize;
}
