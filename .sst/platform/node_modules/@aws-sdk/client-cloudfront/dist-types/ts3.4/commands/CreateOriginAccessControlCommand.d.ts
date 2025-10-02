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
  CreateOriginAccessControlRequest,
  CreateOriginAccessControlResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateOriginAccessControlCommandInput
  extends CreateOriginAccessControlRequest {}
export interface CreateOriginAccessControlCommandOutput
  extends CreateOriginAccessControlResult,
    __MetadataBearer {}
export declare class CreateOriginAccessControlCommand extends $Command<
  CreateOriginAccessControlCommandInput,
  CreateOriginAccessControlCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateOriginAccessControlCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateOriginAccessControlCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateOriginAccessControlCommandInput,
    CreateOriginAccessControlCommandOutput
  >;
  private serialize;
  private deserialize;
}
