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
  UpdateOriginAccessControlRequest,
  UpdateOriginAccessControlResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateOriginAccessControlCommandInput
  extends UpdateOriginAccessControlRequest {}
export interface UpdateOriginAccessControlCommandOutput
  extends UpdateOriginAccessControlResult,
    __MetadataBearer {}
export declare class UpdateOriginAccessControlCommand extends $Command<
  UpdateOriginAccessControlCommandInput,
  UpdateOriginAccessControlCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateOriginAccessControlCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateOriginAccessControlCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateOriginAccessControlCommandInput,
    UpdateOriginAccessControlCommandOutput
  >;
  private serialize;
  private deserialize;
}
