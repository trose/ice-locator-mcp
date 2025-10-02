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
import { DeleteOriginAccessControlRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteOriginAccessControlCommandInput
  extends DeleteOriginAccessControlRequest {}
export interface DeleteOriginAccessControlCommandOutput
  extends __MetadataBearer {}
export declare class DeleteOriginAccessControlCommand extends $Command<
  DeleteOriginAccessControlCommandInput,
  DeleteOriginAccessControlCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteOriginAccessControlCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteOriginAccessControlCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteOriginAccessControlCommandInput,
    DeleteOriginAccessControlCommandOutput
  >;
  private serialize;
  private deserialize;
}
