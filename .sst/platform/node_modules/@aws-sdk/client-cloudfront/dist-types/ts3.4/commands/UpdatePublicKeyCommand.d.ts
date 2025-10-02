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
  UpdatePublicKeyRequest,
  UpdatePublicKeyResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdatePublicKeyCommandInput extends UpdatePublicKeyRequest {}
export interface UpdatePublicKeyCommandOutput
  extends UpdatePublicKeyResult,
    __MetadataBearer {}
export declare class UpdatePublicKeyCommand extends $Command<
  UpdatePublicKeyCommandInput,
  UpdatePublicKeyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdatePublicKeyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdatePublicKeyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UpdatePublicKeyCommandInput, UpdatePublicKeyCommandOutput>;
  private serialize;
  private deserialize;
}
