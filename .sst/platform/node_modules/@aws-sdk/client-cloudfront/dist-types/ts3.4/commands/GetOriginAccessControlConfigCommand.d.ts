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
  GetOriginAccessControlConfigRequest,
  GetOriginAccessControlConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetOriginAccessControlConfigCommandInput
  extends GetOriginAccessControlConfigRequest {}
export interface GetOriginAccessControlConfigCommandOutput
  extends GetOriginAccessControlConfigResult,
    __MetadataBearer {}
export declare class GetOriginAccessControlConfigCommand extends $Command<
  GetOriginAccessControlConfigCommandInput,
  GetOriginAccessControlConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetOriginAccessControlConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetOriginAccessControlConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetOriginAccessControlConfigCommandInput,
    GetOriginAccessControlConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
